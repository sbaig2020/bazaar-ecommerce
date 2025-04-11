# Bazaar E-commerce Platform

**Note: This is just an experimental project.**

Bazaar is an e-commerce platform designed to provide a seamless shopping experience for customers while making it easy for business owners to manage their online store.

## Features

- Responsive design that works on mobile, tablet, and desktop
- Product catalog with categorization (men, women, kids)
- Detailed product pages with image galleries
- Shopping cart functionality
- Checkout process
- Search functionality
- Product data scraping tool

## MVP Components

This MVP (Minimum Viable Product) version includes:

- Homepage with featured products and categories
- Product listing pages with filtering and pagination
- Product detail pages with image gallery and size selection
- Shopping cart functionality
- Checkout process
- Search functionality
- Admin data scraper for product catalog management

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Data Management**: CSV-based storage (can be upgraded to a database in future versions)
- **Data Collection**: Web scraping with Beautiful Soup and Requests

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- pip package manager

### Installation

1. Clone the repository or download the source code
2. Navigate to the project directory:
   ```
   cd bazaar_site
   ```

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5000
   ```

### Data Collection

To populate the product catalog:

1. Run the product scraper:
   ```
   python scraper/product_scraper.py
   ```

2. This will generate product data in the `data` directory that will be automatically used by the web application.

## Directory Structure

```
bazaar_site/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── data/                  # Product data storage
│   └── bazaar_products.csv
│
├── scraper/               # Product data scraper
│   └── product_scraper.py
│
├── static/                # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
└── templates/             # HTML templates
    ├── base.html
    ├── index.html
    ├── products.html
    ├── product_detail.html
    ├── cart.html
    ├── checkout.html
    └── search_results.html
```


## License

This project is for demonstration purposes only.
