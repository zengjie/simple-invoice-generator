let invoiceItems = [];

document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('invoice_date').value = today;
    updateDueDate(); // This will set the initial due date
    updateSummaries();
    renderInvoiceItems();
    updateInvoicePreview(); // Add this line to update the preview when the page loads
    setupInfoToggle();
    setupEventListeners();
});

function updateSummaries() {
    document.getElementById('customer-summary').textContent = `${document.getElementById('customer_name').value}, ${document.getElementById('city_country').value}`;
    document.getElementById('company-summary').textContent = `${document.getElementById('company_name').value}, ${document.getElementById('company_city_country').value}`;
    document.getElementById('bank-summary').textContent = `${document.getElementById('bank_name').value}, ${document.getElementById('swift_code').value}, ${document.getElementById('account_number').value}`;
    saveToLocalStorage();
}

function showPopup(formId) {
    const popupOverlay = document.getElementById('popup-overlay');
    const popupContent = document.getElementById('popup-content');
    
    let formHtml = '';
    if (formId === 'customer-form') {
        formHtml = `
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Edit Customer Information</h3>
                <button type="button" onclick="closePopup()" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <form id="customer-form">
                <input type="text" name="customer_name" placeholder="Customer Name" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('customer_name').value}">
                <input type="text" name="address_line1" placeholder="Address Line 1" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('address_line1').value}">
                <input type="text" name="address_line2" placeholder="Address Line 2" class="w-full px-3 py-2 border rounded mb-2" value="${document.getElementById('address_line2').value}">
                <input type="text" name="city_country" placeholder="City, Country" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('city_country').value}">
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300">Save</button>
            </form>
        `;
    } else if (formId === 'company-form') {
        formHtml = `
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Edit Company Information</h3>
                <button type="button" onclick="closePopup()" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <form id="company-form">
                <input type="text" name="company_name" placeholder="Company Name" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('company_name').value}">
                <input type="text" name="company_tagline" placeholder="Company Tagline" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('company_tagline').value}">
                <input type="text" name="company_address_line1" placeholder="Address Line 1" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('company_address_line1').value}">
                <input type="text" name="company_address_line2" placeholder="Address Line 2" class="w-full px-3 py-2 border rounded mb-2" value="${document.getElementById('company_address_line2').value}">
                <input type="text" name="company_city_country" placeholder="City, Country" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('company_city_country').value}">
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300">Save</button>
            </form>
        `;
    } else if (formId === 'bank-form') {
        formHtml = `
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Edit Bank Details</h3>
                <button type="button" onclick="closePopup()" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <form id="bank-form">
                <input type="text" name="bank_name" placeholder="Bank Name" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('bank_name').value}">
                <input type="text" name="swift_code" placeholder="SWIFT Code" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('swift_code').value}">
                <input type="text" name="account_number" placeholder="Account Number" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('account_number').value}">
                <input type="text" name="bank_address" placeholder="Bank Address" class="w-full px-3 py-2 border rounded mb-2" required value="${document.getElementById('bank_address').value}">
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300">Save</button>
            </form>
        `;
    }

    popupContent.innerHTML = formHtml;
    popupOverlay.classList.remove('hidden');

    const form = popupContent.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                const input = document.getElementById(key);
                if (input) {
                    input.value = value;
                }
            }
            closePopup();
            updateSummaries();

            // Trigger the invoice preview update
            document.getElementById('invoice-form').dispatchEvent(new Event('change'));
        });
    }
}

function closePopup() {
    document.getElementById('popup-overlay').classList.add('hidden');
}

function renderInvoiceItems() {
    const container = document.getElementById('invoice-items-container');
    container.innerHTML = '';
    invoiceItems.forEach((item, index) => {
        const itemElement = document.createElement('div');
        itemElement.className = 'mb-2 p-2 border rounded';
        itemElement.innerHTML = `
            <input type="text" name="item_${index}" placeholder="Item" class="w-full px-3 py-2 border rounded mb-1" required value="${item.item}" onchange="updateInvoiceItem(${index}, 'item', this.value)">
            <input type="number" name="amount_${index}" placeholder="Amount" class="w-full px-3 py-2 border rounded mb-1" required value="${item.amount}" onchange="updateInvoiceItem(${index}, 'amount', this.value)">
            <input type="text" name="comments_${index}" placeholder="Comments" class="w-full px-3 py-2 border rounded mb-1" value="${item.comments}" onchange="updateInvoiceItem(${index}, 'comments', this.value)">
            <button type="button" class="mt-1 px-2 py-1 bg-red-500 text-white text-xs font-medium rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300" onclick="removeInvoiceItem(${index})">
                Remove
            </button>
        `;
        container.appendChild(itemElement);
    });
    updateInvoiceItemsInput();
}

function addInvoiceItem() {
    invoiceItems.push({ item: '', amount: 0, comments: '' });
    renderInvoiceItems();
    updateInvoicePreview(); // Add this line to update the preview when an item is added
    saveToLocalStorage();
}

function updateInvoiceItem(index, field, value) {
    invoiceItems[index][field] = field === 'amount' ? parseFloat(value) : value;
    updateInvoiceItemsInput();
    updateInvoicePreview(); // Add this line to update the preview when an item is updated
    saveToLocalStorage();
}

function removeInvoiceItem(index) {
    invoiceItems.splice(index, 1);
    renderInvoiceItems();
    updateInvoicePreview(); // Add this line to update the preview when an item is removed
    saveToLocalStorage();
}

function updateInvoiceItemsInput() {
    document.getElementById('invoice_items').value = JSON.stringify(invoiceItems);
}

function saveToLocalStorage() {
    const formData = new FormData(document.getElementById('invoice-form'));
    const data = Object.fromEntries(formData.entries());
    data.invoiceItems = invoiceItems;
    localStorage.setItem('invoiceData', JSON.stringify(data));
}

function loadFromLocalStorage() {
    const savedData = localStorage.getItem('invoiceData');
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = document.getElementById(key);
            if (input) {
                input.value = data[key];
            }
        });
        invoiceItems = data.invoiceItems || [];
        updateInvoiceItemsInput(); // Add this line to ensure the hidden input is updated
    }
}

function updateInvoicePreview() {
    // Trigger the invoice preview update using htmx
    htmx.trigger('#invoice-form', 'change');
}

document.getElementById('popup-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        closePopup();
    }
});

// Add event listener to save data when form changes
document.getElementById('invoice-form').addEventListener('change', saveToLocalStorage);

// Add this new function to handle the upload result
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'upload-result') {
        const response = JSON.parse(event.detail.xhr.responseText);
        if (response.success && response.data) {
            populateFormWithUploadedData(response.data);
            document.getElementById('upload-result').innerHTML = '<p class="text-green-600 font-semibold">Invoice data loaded successfully!</p>';
        } else {
            document.getElementById('upload-result').innerHTML = `<p class="text-red-600 font-semibold">${response.message}</p>`;
            resetDropZone();
        }
        // Scroll to the upload result
        document.getElementById('upload-result').scrollIntoView({ behavior: 'smooth' });
    }
});

function populateFormWithUploadedData(data) {
    // Populate form fields with the extracted data
    document.getElementById('invoice_date').value = data.invoice_date;
    document.getElementById('due_date').value = data.invoice_date; // Assuming due date is the same as invoice date
    document.getElementById('customer_name').value = data.customer_info.name;
    document.getElementById('address_line1').value = data.customer_info.address_line1;
    document.getElementById('address_line2').value = data.customer_info.address_line2;
    document.getElementById('city_country').value = data.customer_info.city_country;
    
    document.getElementById('company_name').value = data.company_info.name;
    document.getElementById('company_tagline').value = data.company_info.tagline;
    document.getElementById('company_address_line1').value = data.company_info.address_line1;
    document.getElementById('company_address_line2').value = data.company_info.address_line2;
    document.getElementById('company_city_country').value = data.company_info.city_country;
    
    document.getElementById('bank_name').value = data.bank_details.beneficiary_bank;
    document.getElementById('swift_code').value = data.bank_details.swift_code;
    document.getElementById('account_number').value = data.bank_details.account_number;
    document.getElementById('bank_address').value = data.bank_details.bank_address;
    
    // Populate invoice items
    invoiceItems = data.items.map(item => ({
        item: item.item,
        amount: item.amount,
        comments: item.comments
    }));
    renderInvoiceItems();
    
    updateSummaries();
    updateInvoicePreview();            
}

// Add these new functions to handle drag and drop
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('drop-zone').classList.add('bg-gray-100');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('drop-zone').classList.remove('bg-gray-100');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('drop-zone').classList.remove('bg-gray-100');

    const dt = e.dataTransfer;
    const files = dt.files;

    handleFiles(files);
}

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type === "application/pdf") {
            document.getElementById('file-upload').files = files;
            showSelectedFile(file.name);
            document.getElementById('upload-form').requestSubmit();
        } else {
            alert("Please upload a PDF file.");
        }
    }
}

function showSelectedFile(fileName) {
    document.getElementById('drop-zone-content').classList.add('hidden');
    document.getElementById('file-selected').classList.remove('hidden');
    document.getElementById('selected-file-name').textContent = fileName;
    document.getElementById('drop-zone').classList.add('bg-green-50', 'border-green-500');
}

function resetDropZone() {
    document.getElementById('drop-zone-content').classList.remove('hidden');
    document.getElementById('file-selected').classList.add('hidden');
    document.getElementById('drop-zone').classList.remove('bg-green-50', 'border-green-500');
    document.getElementById('file-upload').value = '';
}

// Set up the event listeners for drag and drop
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('dragover', handleDragOver);
dropZone.addEventListener('dragleave', handleDragLeave);
dropZone.addEventListener('drop', handleDrop);

// Handle file selection via the file input
document.getElementById('file-upload').addEventListener('change', function(e) {
    handleFiles(this.files);
});

function showDuplicatePopup() {
    document.getElementById('duplicate-popup').classList.remove('hidden');
}

function closeDuplicatePopup() {
    document.getElementById('duplicate-popup').classList.add('hidden');
    resetDropZone();
}

// Add this new function to handle the info toggle
function setupInfoToggle() {
    const infoToggle = document.getElementById('info-toggle');
    const infoText = document.getElementById('info-text');
    let hasSeenInfo = localStorage.getItem('hasSeenInfo');

    if (!hasSeenInfo) {
        infoText.style.display = 'block';
        localStorage.setItem('hasSeenInfo', 'true');

        // Hide the info text after 10 seconds
        setTimeout(function() {
            infoText.style.display = 'none';
        }, 10000);
    } else {
        infoText.style.display = 'none';
    }

    infoToggle.addEventListener('click', function() {
        if (infoText.style.display === 'none') {
            infoText.style.display = 'block';
        } else {
            infoText.style.display = 'none';
        }
    });
}

// Add this function to your script.js file
function updateDueDate() {
    const invoiceDateInput = document.getElementById('invoice_date');
    const dueDateInput = document.getElementById('due_date');
    const dueDateError = document.getElementById('due-date-error');

    if (invoiceDateInput.value) {
        const invoiceDate = new Date(invoiceDateInput.value);
        let dueDate = new Date(invoiceDate.getFullYear(), invoiceDate.getMonth(), 26);

        // If the invoice date is on or after the 26th, set due date to the next day
        if (invoiceDate.getDate() >= 26) {
            dueDate = new Date(invoiceDate.getTime());
            dueDate.setDate(invoiceDate.getDate() + 1);
        }

        // Format the date as YYYY-MM-DD for the input field
        const formattedDueDate = dueDate.toISOString().split('T')[0];
        
        // Only apply the highlight if the due date has changed
        if (dueDateInput.value !== formattedDueDate) {
            dueDateInput.value = formattedDueDate;
            
            // Add the highlight class
            dueDateInput.classList.add('highlight-fade');
            
            // Remove the highlight class after the animation completes
            setTimeout(() => {
                dueDateInput.classList.remove('highlight-fade');
            }, 3000); // 3000ms = 3 seconds, matching our CSS animation duration
        }
    }

    validateDueDate();
}

function validateDueDate() {
    const invoiceDateInput = document.getElementById('invoice_date');
    const dueDateInput = document.getElementById('due_date');
    const dueDateError = document.getElementById('due-date-error');

    if (invoiceDateInput.value && dueDateInput.value) {
        const invoiceDate = new Date(invoiceDateInput.value);
        const dueDate = new Date(dueDateInput.value);

        if (dueDate < invoiceDate) {
            dueDateInput.classList.add('border-red-500');
            dueDateError.textContent = 'Due date cannot be earlier than the invoice date.';
            dueDateError.classList.remove('hidden');
        } else {
            dueDateInput.classList.remove('border-red-500');
            dueDateError.classList.add('hidden');
        }
    }
}

function setupEventListeners() {
    // Remove existing event listeners before adding new ones
    const invoiceDateInput = document.getElementById('invoice_date');
    const dueDateInput = document.getElementById('due_date');
    
    invoiceDateInput.removeEventListener('change', handleInvoiceDateChange);
    dueDateInput.removeEventListener('change', handleDueDateChange);

    // Add new event listeners
    invoiceDateInput.addEventListener('change', handleInvoiceDateChange);
    dueDateInput.addEventListener('change', handleDueDateChange);
}

function handleInvoiceDateChange() {
    updateDueDate();
    updateInvoicePreview();
}

function handleDueDateChange() {
    validateDueDate();
    updateInvoicePreview();
}

// Make sure to call setupEventListeners() when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('invoice_date').value = today;
    updateDueDate(); // This will set the initial due date
    updateSummaries();
    renderInvoiceItems();
    updateInvoicePreview();
    setupInfoToggle();
    setupEventListeners();
});