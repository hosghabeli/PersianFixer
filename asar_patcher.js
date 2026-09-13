const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const asar = require('@electron/asar');
const { flipFuses, FuseVersion, FuseV1Options, getCurrentFuseWire, pathToFuseFile } = require('@electron/fuses');

async function patchAntigravityAsar(srcAsar, destAsar, engineCode) {
    const tempExtract = path.join(process.env.TEMP, 'ag_patch_extract_' + Date.now());
    const tempPacked = path.join(process.env.TEMP, 'ag_patch_pack_' + Date.now() + '.asar');

    if (fs.existsSync(tempExtract)) fs.rmSync(tempExtract, { recursive: true, force: true });
    if (fs.existsSync(tempPacked)) fs.unlinkSync(tempPacked);

    asar.extractAll(srcAsar, tempExtract);

    const preloadPath = path.join(tempExtract, 'dist', 'preload.js');
    let content = fs.readFileSync(preloadPath, 'utf8');

    if (!content.includes('PersianFixer')) {
        content += '\n;\n// --- PERSIAN FIXER ENGINE INJECTION ---\n' + engineCode + '\n';
        fs.writeFileSync(preloadPath, content, 'utf8');
    }

    await asar.createPackageWithOptions(tempExtract, tempPacked, {
        unpack: '**/node_modules/chrome-devtools-mcp/**'
    });

    fs.rmSync(tempExtract, { recursive: true, force: true });

    // Atomic replace
    if (fs.existsSync(destAsar)) fs.unlinkSync(destAsar);
    fs.renameSync(tempPacked, destAsar);
}

function patchAsarExactOffset(srcAsar, destAsar, pathParts, modifier) {
    const raw = asar.getRawHeader(srcAsar);
    const header = JSON.parse(JSON.stringify(raw.header));
    const originalHeaderSize = raw.headerSize;
    const baseOffset = 8 + originalHeaderSize;

    const srcFd = fs.openSync(srcAsar, 'r');
    const srcStat = fs.fstatSync(srcFd);
    const totalDataSize = srcStat.size - baseOffset;

    let curr = header.files;
    for (let i = 0; i < pathParts.length - 1; i++) {
        curr = curr[pathParts[i]].files;
    }
    const fileName = pathParts[pathParts.length - 1];
    const targetEntry = curr[fileName];

    const origBuf = Buffer.alloc(targetEntry.size);
    fs.readSync(srcFd, origBuf, 0, targetEntry.size, baseOffset + parseInt(targetEntry.offset));

    const modifiedContent = modifier(origBuf.toString('utf8'));
    const modifiedBuf = Buffer.from(modifiedContent, 'utf8');

    targetEntry.offset = String(totalDataSize);
    targetEntry.size = modifiedBuf.length;
    if (targetEntry.integrity) {
        const hash = crypto.createHash('sha256').update(modifiedBuf).digest('hex');
        targetEntry.integrity = {
            algorithm: 'SHA256',
            hash: hash,
            blockSize: 4194304,
            blocks: [hash]
        };
    }

    let jsonStr = JSON.stringify(header);
    const origBuf16 = Buffer.alloc(16);
    fs.readSync(srcFd, origBuf16, 0, 16, 0);
    const origJsonLen = origBuf16.readUInt32LE(12);

    const padNeeded = origJsonLen - Buffer.byteLength(jsonStr);
    if (padNeeded < 0) {
        throw new Error(`New header JSON exceeds original JSON length (${origJsonLen}).`);
    }

    const paddingSpaces = ' '.repeat(padNeeded);
    jsonStr = '{"files":' + paddingSpaces + jsonStr.substring('{"files":'.length);

    const headerBlock = Buffer.alloc(16 + origJsonLen + (originalHeaderSize - 8 - origJsonLen));
    origBuf16.copy(headerBlock, 0, 0, 16);
    Buffer.from(jsonStr, 'utf8').copy(headerBlock, 16);

    const tempDest = destAsar + '.tmp';
    const destFd = fs.openSync(tempDest, 'w');
    fs.writeSync(destFd, headerBlock, 0, headerBlock.length);

    const CHUNK_SIZE = 1024 * 1024 * 4;
    const chunk = Buffer.alloc(CHUNK_SIZE);
    let bytesRemaining = totalDataSize;
    let readPos = baseOffset;

    while (bytesRemaining > 0) {
        const toRead = Math.min(bytesRemaining, CHUNK_SIZE);
        const bytesRead = fs.readSync(srcFd, chunk, 0, toRead, readPos);
        fs.writeSync(destFd, chunk, 0, bytesRead);
        readPos += bytesRead;
        bytesRemaining -= bytesRead;
    }

    fs.writeSync(destFd, modifiedBuf, 0, modifiedBuf.length);

    fs.closeSync(srcFd);
    fs.closeSync(destFd);

    if (fs.existsSync(destAsar)) fs.unlinkSync(destAsar);
    fs.renameSync(tempDest, destAsar);
}

async function disableIntegrityFuse(exePath) {
    try {
        const wire = await getCurrentFuseWire(pathToFuseFile(exePath));
        if (wire && wire[FuseV1Options.EnableEmbeddedAsarIntegrityValidation] === 49) {
            await flipFuses(exePath, {
                version: FuseVersion.V1,
                [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: false
            });
            return true;
        }
    } catch (e) {
        // Ignored if already disabled or unsupported
    }
    return false;
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const cmd = args[0];

    (async () => {
        if (cmd === 'check') {
            const asarPath = args[1];
            const pathParts = args[2].split('/');
            try {
                const raw = asar.getRawHeader(asarPath);
                let curr = raw.header.files;
                for (let i = 0; i < pathParts.length - 1; i++) {
                    curr = curr[pathParts[i]].files;
                }
                const entry = curr[pathParts[pathParts.length - 1]];
                const fd = fs.openSync(asarPath, 'r');
                const buf = Buffer.alloc(entry.size);
                fs.readSync(fd, buf, 0, entry.size, 8 + raw.headerSize + parseInt(entry.offset));
                fs.closeSync(fd);
                console.log(buf.toString('utf8').includes('PersianFixer') ? 'PATCHED' : 'UNPATCHED');
            } catch (e) {
                console.log('ERROR: ' + e.message);
            }
        } else if (cmd === 'patch') {
            const srcAsar = args[1];
            const destAsar = args[2];
            const targetFile = args[3];
            const enginePath = args[4];
            const exeToFuse = args[5];

            const engineCode = fs.readFileSync(enginePath, 'utf8');

            try {
                if (targetFile.includes('preload.js')) {
                    // Antigravity
                    await patchAntigravityAsar(srcAsar, destAsar, engineCode);
                } else {
                    // Claude or other padded asar
                    patchAsarExactOffset(srcAsar, destAsar, targetFile.split('/'), (content) => {
                        if (content.includes('PersianFixer')) return content;
                        return content + '\n;\n' + engineCode + '\n';
                    });
                }

                if (exeToFuse && fs.existsSync(exeToFuse)) {
                    await disableIntegrityFuse(exeToFuse);
                }

                console.log('SUCCESS');
            } catch (e) {
                console.error('ERROR: ' + e.message);
                process.exit(1);
            }
        }
    })();
}