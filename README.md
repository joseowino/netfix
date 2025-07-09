# NetFix - Home Services Platform

NetFix is a Django-based web application that connects homeowners with service providers for various home maintenance and improvement needs. The platform facilitates service booking, management, and review processes between customers and service companies.

## Features

### For Customers
- Browse available services by category
- View detailed service information and pricing
- Request services with specific requirements
- Track service request status
- Leave reviews for completed services
- Manage personal profile
- View service history

### For Service Providers
- Create and manage service listings
- Specify service areas and pricing
- Handle service requests
- View customer reviews
- Manage company profile
- Track service history

### Service Categories
- Air Conditioner
- Carpentry
- Electricity
- Gardening
- Home Machines
- House Keeping
- Interior Design
- Locks
- Painting
- Plumbing
- Water Heaters

## Technical Stack

- Python 3.x
- Django 3.1.14
- SQLite (Development)
- HTML/CSS

## Project Structure

```
netfix/
├── main/               # Core application functionality
├── services/           # Service-related features
├── users/              # User management
├── media/              # User-uploaded files
├── static/             # Static files (CSS, images)
└── templates/          # HTML templates
```

## Installation

1. Clone the repository:
```bash
git clone https://learn.zone01kisumu.ke/git/skisenge/netfix.git
cd netfix
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv # alternatively: pip install virtualenv && virtualenv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```
5. Run the development server:
```bash
python manage.py runserver
```

## Testing
```bash
python manage.py test
python manage.py test users -v 2
python manage.py test services -v 2
```

## User Types

1. **Customers**
   - Can browse and request services
   - Can leave reviews
   - Can track service history

2. **Service Providers**
   - Can create service listings
   - Can manage service requests
   - Can view customer reviews

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

## Contact

[joseowino](https://github.com/joseowino)

[vomolo](https://github.com/vomolo)

