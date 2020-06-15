var os = require('os');
var crypto = require('crypto');


function generateId(){
    return getSha256(getMacs()[0]).slice(0, 40);
}

function getSha256(data){
    return crypto.createHash('sha256').update(data).digest('hex');
}

function getMacs() {
    const interfaces = os.networkInterfaces();
    const macs = [];
    Object.keys(interfaces).forEach((netInterface) => {
        interfaces[netInterface].forEach((interfaceObject) => {
            if (['IPv4', 'IPv6'].includes(interfaceObject.family)
                && !interfaceObject.internal
                && !(interfaceObject.mac === '00:00:00:00:00:00')) {
                macs.push(interfaceObject.mac);
            }
        });
    });
    return macs;
}

module.exports.bucketId = generateId;
