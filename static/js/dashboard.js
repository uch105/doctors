function CopyLink(link){
    navigator.clipboard.writeText(link).then(function() {
        alert("Link Copied to clipboard!");
    });
}

function CopyPostLink(link){
    navigator.clipboard.writeText("https://prescribemate.com/dashboard/forum/post/"+link+"/").then(function() {
        alert("Link Copied to clipboard!");
    });
}

function OpenCommentBox(postID){
    document.getElementById("comment-box-"+postID).classList.remove("hide");
}

function likepost(postID){
    fetch('/dashboard/forum/post/'+postID+'/like/')
    .then(response => response.json())
    .then(data => {
        if (data.likes){
            document.getElementById('like-count-'+postID).innerText = data.likes + ' likes';
        } else if (data.error){
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error', error);
    });
}

function ShowLikes(){
    document.getElementById('post-likelist').classList.remove('hide')
}

function ShowCalculator(){
    c_f = document.getElementById('c-feature');
    c_f.classList.add("active");
    i_f = document.getElementById('i-feature');
    i_f.classList.remove("active");
    document.getElementById('c-section').style.display="block";
    document.getElementById('i-section').style.display="none";
}

function ShowInformation(){
    i_f = document.getElementById('i-feature');
    i_f.classList.add("active");
    c_f = document.getElementById('c-feature');
    c_f.classList.remove("active");
    document.getElementById('c-section').style.display="none";
    document.getElementById('i-section').style.display="block";
}

function insertDoseText(){
    document.getElementById('prestext').value += document.getElementById("dosage").value + " ";
    document.getElementById('dosage').selectedIndex = 0;
}

function insertDoseText2(){
    document.getElementById('prestext').value += " - " + document.getElementById("dosage2").value;
    document.getElementById('dosage2').selectedIndex = 0;
}

function insertDoseText3(){
    document.getElementById('prestext').value += " - " + document.getElementById("dosage3").value;
    document.getElementById('dosage3').selectedIndex = 0;
}

function showSG(s){
    for(let i=1; i<3; i++){
        if(i==parseInt(s)){
            document.getElementById("sgb"+s).classList.add("agreen");
            document.getElementById("sgf"+s).classList.remove("hide");
        }
        else{
            document.getElementById("sgb"+i).classList.remove("agreen");
            document.getElementById("sgf"+i).classList.add("hide");
        }
    }
}

function showSS(s){
    var j =document.getElementsByClassName("ss-buttons").length;
    for(let i=1; i<=j; i++){
        if(i==parseInt(s)){
            document.getElementById("ssb"+s).classList.add("agreen");
            document.getElementById("ssf"+s).classList.remove("hide");
        }
        else{
            document.getElementById("ssb"+i).classList.remove("agreen");
            document.getElementById("ssf"+i).classList.add("hide");
        }
    }
}

function addAdviceTemplate(s){
    fetch('/api/search_advice/?query='+s)
        .then(response => response.json())
        .then(data =>{
            var pad = document.getElementById('prestext');
            data.forEach(item => {
                pad.value += '\n\n\nউপদেশঃ\n' + '\t' + item.advice1 + '\n\t' + item.advice2 + '\n\t' + item.advice3 + '\n\t' + item.advice4 + '\n\t' + item.advice5;
            });
        });
}

/*
let printEmbeddedObject = () => {
     
    const getObjectElement = document.querySelector('embed');
    let pdfFileLocation = getObjectElement.getAttribute('src');
    console.log(pdfFileLocation);
   
    let instanceIframeObject = document.createElement('iframe');  
    instanceIframeObject.style.visibility = 'hidden';
    instanceIframeObject.src = pdfFileLocation;

    document.body.appendChild(instanceIframeObject);

    instanceIframeObject.contentWindow.focus();
    instanceIframeObject.contentWindow.print();
}
*/



// -------------- send for preview -------------

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('previewButton').addEventListener('click', function () {
    const formData = new FormData(document.getElementById('prescription'));

    fetch('/api/preview-pdf/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // CSRF token for Django
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {

        // Update the PDF preview
        if (data.pdf_url) {
            var pdfdom = document.getElementById('pdfPreview');
            pdfdom.innerHTML = `<embed src="${data.pdf_url}" id="myFrame" type="application/pdf" width="300" height="400">`;
        }
    })
    .catch(error => console.error('Error:', error));
});

// --------------- Drugs,OE,Ix suggestions -----------------

/*
function setupAutocomplete(inputId, padId, suggestionsId, apiUrl) {
    const inputField = document.getElementById(inputId);
    const padField = document.getElementById(padId);
    const suggestionsDiv = document.getElementById(suggestionsId);

    inputField.addEventListener('input', function () {
        const query = this.value;

        if (query.length > 0) {
            fetch(`${apiUrl}?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsDiv.innerHTML = '';
                    data.forEach(item => {
                        const suggestion = document.createElement('div');
                        suggestion.classList.add('autocomplete-suggestion');
                        if(apiUrl=="/api/search_drug/"){
                            suggestion.textContent = item.brand;
                            suggestion.addEventListener('click', () => {
                                padField.value += item.brand + "\n";
                                suggestionsDiv.innerHTML = '';
                                inputField.value = "";
                            });
                        } else{
                            suggestion.textContent = item.text;
                            suggestion.addEventListener('click', () => {
                                padField.value += item.text + "\n";
                                suggestionsDiv.innerHTML = '';
                            });
                        }
                        suggestionsDiv.appendChild(suggestion);
                    });
                    suggestionsDiv.style.display = "block";
                });
        } else {
            suggestionsDiv.innerHTML = '';
            suggestionsDiv.style.display = "none";
        }
    });
}


setupAutocomplete('drug', 'prestext', 'drugsuggestions', '/api/search_drug/');
setupAutocomplete('oe', 'oe', 'oesuggestions', '/api/search_oe/');
setupAutocomplete('ix', 'ix', 'ixsuggestions', '/api/search_ix/');
*/
function setupAutocomplete(inputId, padId, suggestionsId, apiUrl) {
    const inputField = document.getElementById(inputId);
    const padField = document.getElementById(padId);
    const suggestionsDiv = document.getElementById(suggestionsId);

    inputField.addEventListener('input', function () {
        const query = this.value.split('\n').pop();

        if (query.length > 0) {
            fetch(`${apiUrl}?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsDiv.innerHTML = '';
                    data.forEach(item => {
                        const suggestion = document.createElement('div');
                        suggestion.classList.add('autocomplete-suggestion');
                        
                        suggestion.textContent = item.text;

                        suggestion.addEventListener('click', () => {
                            
                            padField.value = inputField.value.substr(0,inputField.value.length - query.length) + item.text + '\n';
                            //inputField.value = inputField.value.substr(0,inputField.value.length - query.length);
                            suggestionsDiv.innerHTML = '';
                            inputField.focus();
                        });
                        
                        suggestionsDiv.appendChild(suggestion);
                    });
                    suggestionsDiv.style.display = "block";
                });
        } else {
            suggestionsDiv.innerHTML = '';
            suggestionsDiv.style.display = "none";
        }
    });

    inputField.addEventListener('blur', function () {
        setTimeout(() => {
            suggestionsDiv.style.display = "none";
        }, 200);
    });

    inputField.addEventListener('focus', function () {
        const query = this.value.trim();
        if (query.length > 0) {
            suggestionsDiv.style.display = "block";
        }
    });
}

function setupAutocompleteDrug(inputId, padId, suggestionsId, apiUrl) {
    const inputField = document.getElementById(inputId);
    const padField = document.getElementById(padId);
    const suggestionsDiv = document.getElementById(suggestionsId);

    inputField.addEventListener('input', function () {
        const query = this.value;

        if (query.length > 0) {
            fetch(`${apiUrl}?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsDiv.innerHTML = '';
                    data.forEach(item => {
                        const suggestion = document.createElement('div');
                        suggestion.classList.add('autocomplete-suggestion');
                        
                        suggestion.textContent = item.drugs_type + ' ' + item.brand + '(' + item.drugs_dose + ')';

                        suggestion.addEventListener('click', () => {
                            
                            if (padField.value == ''){
                                padField.value += item.drugs_type + ' ' + item.brand + '(' + item.drugs_dose + ')' + "\n";
                            } else{
                                padField.value += "\n\n" + item.drugs_type + ' ' + item.brand + '(' + item.drugs_dose + ')' + "\n";
                            }
                            inputField.value = "";
                            suggestionsDiv.innerHTML = '';
                            inputField.focus();
                        });
                        
                        suggestionsDiv.appendChild(suggestion);
                    });
                    suggestionsDiv.style.display = "block";
                });
        } else {
            suggestionsDiv.innerHTML = '';
            suggestionsDiv.style.display = "none";
        }
    });

    inputField.addEventListener('blur', function () {
        setTimeout(() => {
            suggestionsDiv.style.display = "none";
        }, 300);
    });

    inputField.addEventListener('focus', function () {
        const query = this.value.trim();
        if (query.length > 0) {
            suggestionsDiv.style.display = "block";
        }
    });
}


setupAutocompleteDrug('drug', 'prestext', 'drugsuggestions', '/api/search_drug/');
setupAutocomplete('oe', 'oe', 'oesuggestions', '/api/search_oe/');
setupAutocomplete('ix', 'ix', 'ixsuggestions', '/api/search_ix/');
setupAutocomplete('rf', 'rf', 'rfsuggestions', '/api/search_rf/');
setupAutocomplete('dx', 'dx', 'dxsuggestions', '/api/search_dx/');
setupAutocomplete('cc', 'cc', 'ccsuggestions', '/api/search_cc/');