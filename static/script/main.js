// to show if the file is selected in the form of the home page
function showSelectedFileIcon() {
    var fileInput = document.getElementById("my-file-input");
    var selectedFileIcon = document.getElementById("selected-file-icon");
    
    // Get the file extension
    var fileName = fileInput.value;
    var fileExtension = fileName.split('.').pop().toLowerCase();
    
    // Map file extensions to corresponding icons
    var iconMap = {
        "pdf": "fa-file-pdf",
        "doc": "fa-file-word",
        "docx": "fa-file-word",
        "xls": "fa-file-excel",
        "xlsx": "fa-file-excel",
        "png": "fa-file-image",
        "jpg": "fa-file-image",
        "jpeg": "fa-file-image",
        "gif": "fa-file-image"
    };
    
    // Check if the file extension has a corresponding icon
    if (fileExtension in iconMap) {
        selectedFileIcon.classList.add("active");
        selectedFileIcon.classList.remove("fa-file");
        selectedFileIcon.classList.add(iconMap[fileExtension]);
    } else {
        selectedFileIcon.classList.remove("active");
        selectedFileIcon.classList.remove(iconMap[fileExtension]);
        selectedFileIcon.classList.add("fa-file");
    }
}

const dropdownBtn = document.getElementById('dropdownBtn');
const dropdownMenu = document.getElementById('mobile-menu');
const pv_model_btn = document.querySelector('.btn-label');
const  certificate_text = document.getElementById('certificate_text');
const send_labels = document.getElementById("send_labels")
const send_report = document.getElementById("send_report")

let entities = []



// validation of the home page form
function validateForm(event) {
    event.preventDefault(); // Prevent form submission
    
    var inputField = document.getElementById("model_name");
    var inputValue = inputField.value.trim();
    var errorMessage = document.getElementById("error-message");
    
    if (inputValue === "") {
        errorMessage.innerText = "Error: Input field cannot be empty.";
    } else {
        errorMessage.innerText = "";
        document.getElementById("my-form").submit();
    }
}

// to handle the drop down for phone
dropdownBtn.addEventListener('click', () => {
    dropdownMenu.classList.toggle('h-0');
    dropdownMenu.classList.toggle('hidden');
    dropdownMenu.classList.toggle('transition');
    dropdownMenu.classList.toggle('ease-out');
    dropdownMenu.classList.toggle('duration-300');
    dropdownMenu.classList.toggle('transform');
    dropdownMenu.classList.toggle('opacity-0');
    dropdownMenu.classList.toggle('scale-100');
});

// for the train page to add and remove lables
document.addEventListener('click', (e) => {
    // e.preventDefault()
    // to add the tag arrownd the selected item
    if (e.target.classList.contains("btn-label")){
        const selection = window.getSelection();
        const selectedText = selection.toString();
        let allText = certificate_text.innerText.replace(/<br>/g, ' ');
        allText = allText.replace(/<code>/g, '').replace(/<\/code>/g, '').replace(/<strong>/g, '').replace(/<\/strong>/g, '');
        let starts = []
        let ends = []

        if (selectedText !== '') {
            const range = selection.getRangeAt(0);
            const label = e.target.getAttribute("data-label")
            
            const span = document.createElement('span');
            span.classList.add('selected-text');
            span.classList.add('unselectable');
            span.setAttribute('unselectable',"on");
            span.setAttribute('data-label', label)
            range.surroundContents(span);

            // Calculate start and end indices
            starts = findAllIndices(allText, selectedText)
            starts.forEach(element => {
                ends.push(element + selectedText.length)
            });
            // to add in the entities table
            for (let i=0; i<starts.length; i++){
                if (!is_in(entities, starts[i])){
                    entities.push([starts[i], ends[i], label])
                }
            }
        }
    }

    // to remove the tag from arrownd the selected item
    if (e.target.classList.contains("selected-text")){
        const allText = certificate_text.innerText.replace(/<br>/g, ' ');
        text = e.target.innerText
        starts = findAllIndices(allText, text)
        rm_starts(entities, starts)
        const listItem = e.target
        const newItem = document.createTextNode(text);

        listItem.parentNode.replaceChild(newItem, listItem);
    }

    if(e.target.classList.contains("see-more-detail")){
        const number = e.target.getAttribute("data-number")
        const moreDetail = e.target.parentElement.querySelector(".more-detail"+number)
        moreDetail.classList.toggle("show")
    }

})

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey) {
        key = event.key
        var btn = document.getElementById(`btn-${key}`);
        btn.click()
    }
});

// Function to remove the flash messages after a specified duration
function removeFlashMessages() {
    var flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flashMessage) {
    setTimeout(function() {
        // flashMessage.style.opacity = 0;
        flashMessage.classList.add("flash-message")
        setTimeout(function() {
            flashMessage.remove();
        }, 900); // Duration of fade out animation
      }, 3000); // Duration of flash message display
    });
}

// Call the function when the page has finished loading
window.addEventListener('DOMContentLoaded', function() {
    removeFlashMessages();
});



send_labels.addEventListener('click', () => {
    const final_entities = []
    entities.forEach(element => {
        final_entities.push(`(${element[0]},${element[1]},'${element[2]}')`)
    });
    
    text = certificate_text.innerText.replace(/<br>/g, ' ').replace(/<code>/g, '').replace(/<\/code>/g, '').replace(/<strong>/g, '').replace(/<\/strong>/g, '');
    let starts = []
    if (text != "" && entities.length > 0){
        fetch('/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({text: text, entities: final_entities.toString()}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                window.location.href = "/";
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    else{
        const parentElement = document.getElementById('container');
        const content = `<span class="flash block mb-5 px-7 py-3 w-fit mx-auto text-center bg-red-200 text-red-800 rounded-l text-lg font-bold ">You need to put text and select labels</span>`
        parentElement.insertAdjacentHTML("afterbegin",content)
        removeFlashMessages();
    }
})

send_report.addEventListener('click', () => {
    // const data = 
})

function findAllIndices(str, substring) {
    const indices = [];
    let index = str.indexOf(substring);
    while (index !== -1) {
        indices.push(index);
        index = str.indexOf(substring, index + 1);
    }
    return indices;
}

function is_in(entities, start){
    for (let i =0; i<entities.length; i++){
        if (entities[i][0] == start){
            return true
        }
    }
    return false
}

function rm_starts(entities, starts){
    starts.forEach(start => {
        for (let i=0; i<entities.length; i++){
            if (start == entities[i][0]){
                entities.splice(i, 1)
            }
        }
    });
}