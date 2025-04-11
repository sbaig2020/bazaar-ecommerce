// Bazaar E-commerce - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Product image gallery functionality is handled in product_detail.html
    
    // Back to top button functionality
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Add to cart notification
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            // In a real implementation, this would add the product to cart via AJAX
            // For MVP, we'll just show a notification
            const productId = this.dataset.productId;
            const toast = document.createElement('div');
            toast.className = 'toast show position-fixed bottom-0 end-0 m-4';
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            toast.innerHTML = `
                <div class="toast-header">
                    <strong class="me-auto">Bazaar</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Product added to cart successfully!
                </div>
            `;
            document.body.appendChild(toast);
            
            // Remove toast after 3 seconds
            setTimeout(function() {
                toast.remove();
            }, 3000);
        });
    });
    
    // Newsletter subscription form
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = document.getElementById('newsletter-email');
            const email = emailInput.value.trim();
            
            if (email) {
                // In a real implementation, this would submit the email to a backend service
                // For MVP, we'll just show a success message
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success mt-2';
                successMsg.textContent = `Thank you for subscribing to our newsletter!`;
                newsletterForm.appendChild(successMsg);
                emailInput.value = '';
                
                // Remove success message after 5 seconds
                setTimeout(function() {
                    successMsg.remove();
                }, 5000);
            }
        });
    }
    
    // Product filter collapse on mobile
    const filterToggleBtn = document.getElementById('filter-toggle');
    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', function() {
            const filterContainer = document.getElementById('product-filters');
            filterContainer.classList.toggle('show-filters');
        });
    }
    
    // Countdown timer for special offers
    const countdownElement = document.getElementById('offer-countdown');
    if (countdownElement) {
        const endTime = new Date();
        endTime.setHours(endTime.getHours() + 24);
        
        function updateCountdown() {
            const now = new Date();
            const diff = endTime - now;
            
            if (diff <= 0) {
                countdownElement.textContent = 'Offer expired!';
                return;
            }
            
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            countdownElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }
});

// Product quantity input validation
function validateQuantity(input) {
    const value = parseInt(input.value);
    if (isNaN(value) || value < 1) {
        input.value = 1;
    }
}