 function goBack() {
    window.history.back();
}
 // Funciones del dropdown de usuario
    function menu_usuario() {
        const dropdown = document.getElementById('user-dropdown');
        dropdown.classList.toggle('show');
    }

    window.addEventListener('click', function(event) {
        if (!event.target.matches('#user-icon-btn, #user-icon-btn img')) {
            const dropdowns = document.getElementsByClassName("user-dropdown");
            for (let i = 0; i < dropdowns.length; i++) {
                const openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    });