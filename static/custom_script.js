function adjustSidebarPosition() {
    var mapElement = document.querySelector('.folium-map'); 
    var mapRect = mapElement.getBoundingClientRect(); 

    var sidebar = document.querySelector('.sidebar');
    sidebar.style.top = mapRect.top + mapRect.height * 0.15 + 'px';
    sidebar.style.height =  mapRect.height * 0.75 + 'px';
}
adjustSidebarPosition()

goBtn.onclick = function() {
    var goBtn = document.getElementById("goBtn");
    var model = document.getElementById("dropdown_model").value;
    var topic = document.getElementById("dropdown_topic").value;
    window.location = model+"_"+topic+".html";
}

modeBtn.onclick = function() {
    window.location = "comparison.html";
}

function myStyleFunction(feature, i, t) {
    let colorList;
    if (t === "classification") { colorList = feature.properties.classification_colors;} 
    else if (t === "sentiment") { colorList = feature.properties.sentiment_colors;}
    else {colorList = feature.properties[t];}
    return {
        fillColor: colorList[i],
        color: colorList[i],
    };
}

evaluationButton.onclick = function() {
    const promptVersionElement = document.getElementById('promptVersionMetrics');
    const evaluationMetricsElement = document.getElementById('evluationMetrics');

    // Check if promptVersionMetrics or evluationMetrics is not specified
    if (!promptVersionElement.value || !evaluationMetricsElement.value) {
        return; // Exit the function if either is not specified
    }

    const promptVersion = parseInt(promptVersionElement.value);
    const metric = evaluationMetricsElement.value + '_colors';
    
    for (const countryName in layerDict) {
        const layerName = layerDict[countryName];
        const layer = window[layerName];
        layer.setStyle(function(feature) {
            return myStyleFunction(feature, promptVersion, metric)
        });
        document.getElementById('classificationLegend').style.display = 'none';
        document.getElementById('sentimentLegend').style.display = 'none';
        document.getElementById('evaluationLegend').style.display = 'block'; 
    }
    computeMetrics();
}


function colorByPromptVersion(){
    const promptVersion = parseInt(document.getElementById('promptVersionColor').value);
    for (const countryName in layerDict) {
        const layerName = layerDict[countryName];
        const layer = window[layerName];
        layer.setStyle(function(feature) {
            return myStyleFunction(feature, promptVersion, "classification")
        });
        document.getElementById('sentimentLegend').style.display = 'none';
        document.getElementById('evaluationLegend').style.display = 'none';
        document.getElementById('classificationLegend').style.display = 'block';
        
    }
}

function colorBySentimentPromptVersion(){
    const promptVersion = parseInt(document.getElementById('sentimentPromptVersionColor').value);
    for (const countryName in layerDict) {
        const layerName = layerDict[countryName];
        const layer = window[layerName];
        layer.setStyle(function(feature) {
            return myStyleFunction(feature, promptVersion, "sentiment")
        });
        document.getElementById('classificationLegend').style.display = 'none';
        document.getElementById('evaluationLegend').style.display = 'none';
        document.getElementById('sentimentLegend').style.display = 'block';
    }
}

function computeTFIDF(){
    const threshold = document.getElementById('tfidfThreshold').value;
    const windomhtml = window.location.href.split('/');
    const windowlocs = windomhtml[windomhtml.length - 1];
    const underscoreIndex = windowlocs.indexOf("_");

    const lastModel = windowlocs.substring(0, underscoreIndex);
    const lastTopic = windowlocs.substring(underscoreIndex + 1).split('.')[0];

    $.ajax({
        url: '/tfidf',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({ threshold: threshold, model: lastModel, topic: lastTopic}),
        success: function(response) {
            updateTFIDF(response);
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}

function updateTFIDF(response){

    document.getElementById('tfidf-res').innerHTML = '';

    for (const updated_response of response) {

        const country = updated_response['country']
        const layerID = updated_response['layer_id']
        const responses = updated_response['responses']
        const words = updated_response['selected_words'].join(', ')
        

        const listItem = document.createElement('li');
        const anchor = document.createElement('a');
        const countrySpan = document.createElement('span');
        countrySpan.style.textDecoration = 'underline';
        countrySpan.textContent = country;
        anchor.appendChild(countrySpan);
        anchor.innerHTML += `: ${words}`;

        // Add event listeners to open popup on click
        anchor.addEventListener('click', function() {
            openPopupForCountry(layerID);
        });

        listItem.appendChild(anchor);

        // Append the list items to the respective lists
        document.getElementById('tfidf-res').appendChild(listItem);

 
        const layerName = layerDict[layerID]
        var layer = window[layerName]
        for (const response_id in responses){
            const currResponse = layer.getPopup().getContent().querySelector('#' + response_id);
            currResponse.innerHTML = responses[response_id]
        }
    }
}

function openPopupForCountry(layerID) {
    const layerName  = layerDict[layerID];
    var layer = window[layerName];
    // Open the popup
    layer.openPopup();
}

function computeMetrics(){
    const metric = document.getElementById('evluationMetrics').value;
    const windomhtml = window.location.href.split('/');
    const windowlocs = windomhtml[windomhtml.length - 1];
    const underscoreIndex = windowlocs.indexOf("_");

    const lastModel = windowlocs.substring(0, underscoreIndex);
    const lastTopic = windowlocs.substring(underscoreIndex + 1).split('.')[0];

    $.ajax({
        url: '/metrics',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({metric: metric, model: lastModel, topic: lastTopic}),
        success: function(response) {
            buildMetricTable(response);
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}


function buildMetricTable(response) {
    const ranks = response['ranks']
    const countries = response['countries']
    const scores = response['scores']

    // Get the element where the table will be inserted
    const tableContainer = document.getElementById('metric-table');

    // Clear any existing content inside the container
    tableContainer.innerHTML = '';

    // Create a new table element
    const table = document.createElement('table');

    // Create table header row
    const headerRow = table.createTHead().insertRow();
    const headers = ['Rank', 'Country', 'Score'];

    // Add headers to the header row
    headers.forEach(headerText => {
        const headerCell = document.createElement('th');
        headerCell.textContent = headerText;
        headerRow.appendChild(headerCell);
    });

    // Create table body
    const tableBody = table.createTBody();

    // Populate the table with data from the lists
    for (let i = 0; i < ranks.length; i++) {
        const rowData = [ranks[i], countries[i], scores[i]];

        // Create a new row in the table body
        const row = tableBody.insertRow();

        // Insert cells (columns) into the row
        rowData.forEach(cellData => {
            const cell = row.insertCell();
            cell.textContent = cellData;
        });
    }

    // Append the table to the container element
    tableContainer.appendChild(table);
}


function searchLocation(map) {
    var userInput = document.getElementById('search-input').value;

    if (userInput === '') {
        // Do nothing if the input is blank
        return;
    }

    var windomhtml = window.location.href.split('/');
    var windowlocs = windomhtml[windomhtml.length - 1];
    var underscoreIndex = windowlocs.indexOf("_");

    var lastModel = windowlocs.substring(0, underscoreIndex);
    var lastTopic = windowlocs.substring(underscoreIndex + 1).split('.')[0];

    $.ajax({
        url: '/search',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({ location: userInput, model: lastModel, topic: lastTopic}),
        success: function(response) {
            updateMap(response, map);
            document.getElementById('search-input').value = '';
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}

function updateMap(layers, map) {

    const keyword = layers['keyword']
    const countries_info = layers['country_info']
    const popup_len = layers['popup_len']

    var additional_feature_group_1 = L.featureGroup(
        {}
    ).addTo(map);

    for (const country_info of countries_info) {

        const country = country_info['country']
        const responses = country_info['responses']
        const color = country_info['color']

        const layerName = layerDict[country]

        var layer = window[layerName]
        const clonedLayer = cloneLayerWithPopupAndStyle(layer, color, responses, popup_len);
        clonedLayer.addTo(additional_feature_group_1)
    }

    grouped_layer_control_1.addOverlay(additional_feature_group_1, keyword,"Keywords")
    additional_feature_group_1.remove()
}


function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const resultArray = [];
    for (let i = 0; i < length; i++) {
        resultArray.push(characters.charAt(Math.floor(Math.random() * characters.length)));
    }
    return resultArray.join('');
}

function cloneLayerWithPopupAndStyle(layer, color, responses, popup_len) {
    // Create a new layer with the same geometry
    const clonedLayer = L.GeoJSON.geometryToLayer(layer.toGeoJSON());

    // Copy popup content if exists
    if (layer.getPopup()) {
        const originalPopup = layer.getPopup();

        //Create a new popup with the same content and set the maxWidth
        const clonedPopup = L.popup({
            "maxWidth": 400,  // Set your desired maximum width
        });

        const clonedContent = originalPopup.getContent().cloneNode(true)

        const hash = generateRandomString(32); // Generate a 32-character hash

        // Create a Leaflet popup with a unique variable name
        const popup_var = "popup_" + hash;


        const prevButtonInClonedPopup = clonedContent.querySelector('#prev_button');
        const nextButtonInClonedPopup  = clonedContent.querySelector('#next_button');

        if (prevButtonInClonedPopup != null) {
            prevButtonInClonedPopup.outerHTML = "<button id='prev_button' style='background: none; border: none;' onclick=\"previousResponse('" + popup_var + "')\"><i class='fa fa-chevron-left' aria-hidden='true'></i>  </button>";
            nextButtonInClonedPopup.outerHTML = "<button id='next_button' style='background: none; border: none;' onclick=\"nextResponse('" + popup_var + "')\"> <i class='fa fa-chevron-right' aria-hidden='true'></i> </button>";
        }

        for (const response_id in responses){
            const responseInClonedPopup = clonedContent.querySelector('#' + response_id);
            responseInClonedPopup.innerHTML = responses[response_id]
        }

        

        clonedPopup.setContent(clonedContent);

        // Bind the cloned popup to the cloned layer
        clonedLayer.bindPopup(clonedPopup);

        window[popup_var] = clonedPopup;
        popupDict[popup_var] = [0, popup_len];
    }

    // Set the new style
    const newStyle = {
        'color': color,         
        'fillColor': color
        // Add more style properties as needed
    };

    if (layer.getTooltip()) {
        // Create a new tooltip with the same content
        const originalTooltip = layer.getTooltip();
        const clonedTooltip = L.tooltip();

        // Copy specific properties
        clonedTooltip.setContent(originalTooltip.getContent());
        clonedTooltip.setLatLng(originalTooltip.getLatLng());
        clonedTooltip.options = L.Util.extend({}, originalTooltip.options);

        // Bind the cloned tooltip to the cloned layer
        clonedLayer.bindTooltip(clonedTooltip);
    }

    clonedLayer.setStyle(newStyle);
    
    return clonedLayer;
}

function showResponse(idx, popup) {
    var responseDiv = window[popup].getContent().querySelector('#r' + idx.toString() + '_response');
    responseDiv.style.display = "block";
    /*if (idx == 2) { 
        var plotIframe = responseDiv.querySelector('iframe');
        plotIframe.src = plotIframe.getAttribute('src');
    }*/
}

function hideResponse(idx, popup) {
    window[popup].getContent().querySelector('#r'+idx.toString()+'_response').style.display = "none";
}

function previousResponse(popup) {
    currentResponse = popupDict[popup][0];
    responsesCount = popupDict[popup][1];
    hideResponse(currentResponse, popup);
    currentResponse = (currentResponse - 1 + responsesCount) % responsesCount;
    showResponse(currentResponse, popup);
    popupDict[popup][0] = currentResponse;
}

function nextResponse(popup) {
    currentResponse = popupDict[popup][0];
    responsesCount = popupDict[popup][1];
    hideResponse(currentResponse, popup);
    currentResponse = (currentResponse + 1) % responsesCount;
    showResponse(currentResponse, popup);
    popupDict[popup][0] = currentResponse;
}