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
}

function insertDoseText2(){
    document.getElementById('prestext').value += " - " + document.getElementById("dosage2").value;
}

function insertDoseText3(){
    document.getElementById('prestext').value += " - " + document.getElementById("dosage3").value + "\n";
}

function showSG(s){
    for(let i=1; i<5; i++){
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

const drugInput = document.getElementById('drug');
const suggestionsDiv = document.getElementById('suggestions');

drugInput.addEventListener('input', function() {
    const query = this.value;

    if (query.length > 1) {
        fetch(`/api/search_drug/?query=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsDiv.innerHTML = '';
                data.forEach(drug => {
                    var type = "";
                    if(drug.drugs_type=="Injection"){
                        type = "Inj.";
                    }
                    else if(drug.drugs_type=="Tablet"){
                        type = "Tab.";
                    }
                    else if(drug.drugs_type=="Syrup"){
                        type = "Syr.";
                    }
                    else if(drug.drugs_type=="Capsule"){
                        type = "Cap.";
                    }
                    else if(drug.drugs_type=="Suppository"){
                        type = "Supp.";
                    }
                    else{
                        type = drug.drugs_type;
                    }
                    const suggestion = document.createElement('div');
                    suggestion.classList.add('autocomplete-suggestion');
                    suggestion.textContent = type+" "+drug.brand;
                    suggestion.addEventListener('click', () => {
                        document.getElementById('prestext').value += "\n" + type + " " + drug.brand + "\n";
                        suggestionsDiv.innerHTML = '';
                    });
                    suggestionsDiv.appendChild(suggestion);
                });
            });
    } else {
        suggestionsDiv.innerHTML = '';
    }
});