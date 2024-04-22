document.addEventListener("DOMContentLoaded", () => {
    const $nav = document.querySelector("#mobile-nav")
    const $toggleNav = $nav.querySelector("#toggle-nav")
    const $navMenu = $nav.querySelector("#nav-menu")

    $toggleNav.addEventListener("click", () => {
        $navMenu.classList.toggle("d-none")
    })
})