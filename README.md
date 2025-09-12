route-planner/
├── cdk/                                # Infrastructure as Code (AWS CDK, IaC demo only)
│   ├── app.py
│   └── routing_stack.py                # API Gateway + Lambda definition
│
├── src/
│   └── journey_service/                # Core service logic
│       ├── __init__.py
│       ├── handler.py                  # Lambda entrypoint (Powertools)
│       ├── digitransit.py              # get_coordinates, query_journeys
│       ├── filters.py                  # filter_journeys
│       ├── notifier.py                 # send_email
│       ├── utils.py                    # time conversions
│       └── config.py                   # loads .env.{env} for dev/demo/preprod
│
├── tests/                              # Unit tests with pytest
│   ├── test_digitransit.py
│   ├── test_filters.py
│   └── test_handler.py
│
├── .env.dev                            # Local developer testing
├── .env.demo                           # Demo environment
├── .env.preprod                        # Pre-production/staging
│
├── sonar-project.properties             # SonarQube config
├── requirements.txt                     # Python dependencies
├── template.yaml                        # SAM template (run locally with `sam local start-api`)
├── README.md                            # Documentation (setup, curl examples, diagrams)
│
└── .github/
    └── workflows/
        └── ci-cd.yml                   # GitHub Actions CI/CD (build, test, sonar, deploy local/demo)
