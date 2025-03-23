document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const form = document.getElementById('preferences-form');
    const spiceLevel = document.getElementById('spice-level');
    const spiceValueDisplay = document.getElementById('spice-value-display');
    const recommendationsContainer = document.getElementById('recommendations-container');
    const loadingElement = document.getElementById('loading');
    const noResultsElement = document.getElementById('no-results');
    const receiptContainer = document.getElementById('receipt-container');
    const receiptDate = document.getElementById('receipt-date');
    const newRecommendationsBtn = document.getElementById('new-recommendations');
    const tryAgainBtn = document.getElementById('try-again');
    const printReceiptBtn = document.getElementById('print-receipt');
    const savePdfBtn = document.createElement('button');
    savePdfBtn.textContent = 'Save as PDF';
    savePdfBtn.classList.add('btn', 'primary');
    savePdfBtn.id = 'save-pdf';
    receiptContainer.appendChild(savePdfBtn);
    const totalPriceElement = document.createElement('div');
    totalPriceElement.id = 'total-price';
    recommendationsContainer.appendChild(totalPriceElement);

    const receiptSound = new Audio('/static/sounds/cash-register.mp3');

    // Update spice level display
    spiceLevel.addEventListener('input', function() {
        spiceValueDisplay.textContent = this.value;
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        recommendationsContainer.innerHTML = '';
        totalPriceElement.textContent = '';
        receiptContainer.classList.add('hidden');
        noResultsElement.classList.add('hidden');
        loadingElement.classList.remove('hidden');

        setTimeout(() => {
            const mockRecommendations = generateMockRecommendations();
            loadingElement.classList.add('hidden');
            if (mockRecommendations.length === 0) {
                noResultsElement.classList.remove('hidden');
            } else {
                receiptContainer.classList.remove('hidden');
                displayRecommendations(mockRecommendations);
                receiptSound.play();
            }
        }, 1500);
    });

    function displayRecommendations(recommendations) {
        recommendationsContainer.innerHTML = '';
        let totalPrice = 0;
        recommendations.forEach(item => {
            totalPrice += item.price;
            const receiptItemHTML = `
                <div class='receipt-item'>
                    <div class='item-name'>${item.name}</div>
                    <div class='item-price'>$${item.price.toFixed(2)}</div>
                </div>
            `;
            recommendationsContainer.innerHTML += receiptItemHTML;
        });
        totalPriceElement.innerHTML = `<strong>Total: $${totalPrice.toFixed(2)}</strong>`;
    }

    printReceiptBtn.addEventListener('click', function() {
        window.print();
    });

    savePdfBtn.addEventListener('click', function() {
        html2canvas(receiptContainer).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const doc = new jsPDF();
            doc.addImage(imgData, 'PNG', 10, 10);
            doc.save('receipt.pdf');
        });
    });
});
