const fs = require('fs');

let json = JSON.parse(fs.readFileSync('test.json'));

let new_json = [];

for (let a of json["addresses"]) {
    let entry = {
        "address": a["address1"],
        "latitude": a["coordinates"]["lat"],
        "longitude": a["coordinates"]["lng"]
    }
    new_json.push(entry);
}

fs.writeFileSync("output.json", JSON.stringify(new_json));