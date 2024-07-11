document.addEventListener('DOMContentLoaded', () => {
        // Your script code here
    // Get all buttons with class "btn-close"
    const closeButtonList = document.querySelectorAll('.close-note');
    console.log(closeButtonList);
    
    // Attach event listeners to each button
    closeButtonList.forEach(button => {
        // Extract note ID from the button's ID
        const noteId = button.id.split('-')[1];
        // Attach the event listener to call deleteNote function
        button.addEventListener('click', () => deleteNote(noteId));
    });
    
    
    const deleteNote = (noteId) => {
        console.log('deleteNote', noteId)
        fetch('/delete-note',{
            method: 'POST',
            body: JSON.stringify({ noteId: noteId })
        }).then((_res) => {
            window.location.href = "/";
        })
    }
    
    const deleteProduct = (itemId) => {
        fetch('/delete-product',{
            method:'POST',
            body: JSON.stringify({ itemId: itemId})
        }).then((_res) => {
            window.location.href = "/catalog";
        })
    }
});





