require('dotenv').config();

const fs = require('fs');
const util = require('util');
const stream = require('stream');
const prettyHrtime = require('pretty-hrtime');
const progress = require('progress');
const Readable = require('stream').Readable;
const UserAgent = require('user-agents');
const ndjson = require('iterable-ndjson');
const jsonToCsv = require('json-to-csv-stream');
const fetch = require('node-fetch');
const once = require('events').once;
const path = require('path');

const userAgent = new UserAgent();

const finished = util.promisify(stream.finished);
const pipeline = util.promisify(stream.pipeline);

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const outcome = (promise) => {
    return promise
        .then(result => ({
            success: true,
            result
        }))
        .catch(error => ({
            success: false,
            error
        }));
};

async function streamToCSV(data, target, skip = 0) {
    const readable = new Readable();
    data.forEach(item => readable.push(JSON.stringify(item)));
    readable.push(null);

    const csv = (skip === 0) ? {
        sendHeaders: true
    } : {
        sendHeaders: false
    };

    await pipeline(
        readable,
        jsonToCsv({
            csv
        }),
        fs.createWriteStream(target, {
            flags: 'a'
        })
    );
}

async function streamToNdJson(data, target) {
    const writable = fs.createWriteStream(target, {
        flags: 'a'
    });

    for await (const chunk of ndjson.stringify(data)) {
        if (!writable.write(chunk)) {
            await once(writable, 'drain');
        }
    }

    writable.end();

    await finished(writable);
}

async function get(opt, skip = 0, bar = null, out = []) {

    const {
        paging,
        ...options
    } = opt.payload;

    options.paging = {
        limit: 100,
        skip
    };

    const res = await fetch(`https://${process.env.HOST_NAME}/v1/identification?api_token=${process.env.API_KEY}`, {
        method: 'POST',
        headers: {
            'user-agent': userAgent.random().data.userAgent,
            'content-type': 'application/json'
        },
        body: JSON.stringify(options)
    });

    const data = await res.json();

    if (data.error) {
        console.log(data.message);
        return out;
    }

    if (data.users.length) {

        if (skip === 0) {
            bar = new progress('Collecting profiles :bar :current/:total influencers :percent', {
                width: 20,
                total: data.total
            });
        }

        const content = data.users.map(item => {
            const {
                match,
                picture,
                ...rest
            } = item;
            return rest;
        });

        out = [...out, ...content];

        if (process.env.CSV === 'true') {
            await streamToCSV(content, `${process.env.OUTPUT_DIR}/${opt.id}.csv`, skip);
        }

        if (process.env.NDJSON === 'true') {
            await streamToNdJson(content, `${process.env.OUTPUT_DIR}/${opt.id}.jsonl`);
        }

        bar.tick(content.length);
        await timeout(500);

        skip = skip + 100;
        return get(opt, skip, bar, out);
    }

    return out;

}

(async () => {
    const start = process.hrtime();
    const file = path.normalize(process.env.SOURCE);
    const payload = await outcome(fs.promises.readFile(file));
    if (!payload.success) {
        return console.log(payload.error.message);
    }
    const data = await get({
        id: path.basename(file, path.extname(file)),
        payload: JSON.parse(payload.result.toString())
    });
    const end = process.hrtime(start);
    console.log(`Collected all profiles in ${prettyHrtime(end)} for: ${data.length} influencers`);
})();