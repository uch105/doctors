function ShowLogin(){
    document.getElementById("login").classList.remove("hide");
    document.getElementById("signin").classList.add("hide");
    document.getElementById("reset").classList.add("hide");
}

function ShowSignin(){
    document.getElementById("signin").classList.remove("hide");
    document.getElementById("login").classList.add("hide");
    document.getElementById("reset").classList.add("hide");
}

function ShowForgetPassword(){
    document.getElementById("reset").classList.remove("hide");
    document.getElementById("login").classList.add("hide");
    document.getElementById("signin").classList.add("hide");
}