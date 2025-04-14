# RadMan
*A Deadline Driven Dev Production featuring: Tomáš Červeň, Bára Tížková, Štěpán Venclík, and Natália Verkinová*

A PoC tool to find optimal patient schedule for PET/CT patients given radionuclides delivery times, various procedures, compounds and patients.

Made for Rakathon 2025, Prague

## Demo
~~A Demo version of this app is (as of 11:45 13.04.2025) running at: https://radman.venclik.eu/~~

## Instalation and Deployment

### Requirements
- Python 3.11+
- npm

### Deployment (Dev Version)
Clone the repository:
```shell
git clone https://github.com/oberth-effect/rackathon-radman.git
cd rackathon-radman
```
Install requirements
```
python3 -m .venv
# Activate the .venv
source .venv/bin/activate # OR based on your system
# Install requirements
pip install -r requirements.txt
```
Build Tailwind assets:
```
python manage.py tailwind install

python manage.py tailwind build # OR `tailwind start` for continuous rebuilds
```
Run DevServer:
```
python manage.py runserver
```
> [!CAUTION]
> For production deployments, see https://docs.djangoproject.com/en/5.1/howto/deployment/

## Logic
The solver was created outside Django web app. The folder `sandbox/` contains standalone scripts that solve the Schedule, 
and includes some features not yet implemented in the WebApp.

## License
The Program is licensed under the terms of the [CRAPL License](https://matt.might.net/articles/crapl/); upon request, a relicensing under the [GLWTPL License](https://github.com/me-shaon/GLWTPL) will be provided.
> [!NOTE]
> In all seriousness, if you find any of this even remotely useful, please treat this as if it is under the MIT license and do not hesitate to reach out. The code is not very polished, but we are happy to explain the ideas behind it.

