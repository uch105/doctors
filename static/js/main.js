let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.remove('active');
        if (i === index) {
            slide.classList.add('active');
        }
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
}

setInterval(nextSlide, 2000); // Change slide every 2 seconds

document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
});


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