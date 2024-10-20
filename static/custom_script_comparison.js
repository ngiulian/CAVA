modeBtn.onclick = function() {
    window.location = "entry.html";
}

function requestToBuildMap() {
    const model1 = document.getElementById("dropdown_model_1").value;
    const model2 = document.getElementById("dropdown_model_2").value;
    const topic = document.getElementById("dropdown_topic").value;
    const pv = document.getElementById("dropdown_prompt_version").value;

    if (!model1 || !model2 || !topic || !pv){
        return;
    }

    $.ajax({
        url: '/comparison',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({ model1 : model1, model2: model2, topic: topic, pv: pv}),
        success: function(response) {
            updateMap2(response);
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}

function updateMap2(response) {
    // Assuming response contains layer IDs as keys and an object with 'color', 'response_1', and 'response_2' as values
    for (const layerid in response) {
        const layerName = layerDict[layerid];
        var layer = window[layerName];
        const color = response[layerid]['color'];

        const newStyle = {
            'color': color,
            'fillColor': color
        };
        layer.setStyle(newStyle);

        const model_1_res = layer.getPopup().getContent().querySelector('#model_1_response');
        model_1_res.innerHTML = response[layerid]['response_1'];
        const model_2_res = layer.getPopup().getContent().querySelector('#model_2_response');
        model_2_res.innerHTML = response[layerid]['response_2'];
        const prompt_class = layer.getPopup().getContent().querySelector('#prompt_classification');
        prompt_class.innerHTML = response[layerid]['prompt_classification'];
        const prompt_open = layer.getPopup().getContent().querySelector('#prompt_open_ended');
        prompt_open.innerHTML = response[layerid]['prompt_open_ended'];
    }
}