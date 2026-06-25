function render({model, el}) {
    console.log(model.get('app'));
    for (const [key, value] of Object.entries(model.get('app'))) {
        for (const [subKey, subValue] of Object.entries(value)) {
            console.log(`Key: ${subKey}, Value: ${JSON.stringify(subValue)}`);
        }
    }
}

export default {render};