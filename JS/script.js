x = document.querySelector(".number-but");
function increase() {
  x.innerHTML = eval(x.innerHTML + "+1");
}
function reset() {
  x.innerHTML = 0;
}
