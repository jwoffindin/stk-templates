# Update python packages for lambda-layers; using DOCKER_DEFAULT_PLATFORM to avoid
# issues with building on mac-silicon.
# TODO: extend to support 3.13 — requires separate site-packages per runtime since
# compiled extensions (e.g. cryptography) are Python-version-specific.
setup:
	rm -rf site-packages
	DOCKER_DEFAULT_PLATFORM=linux/amd64 docker run --rm -it --entrypoint '' -v $(PWD):/app -w /app public.ecr.aws/lambda/python:3.12 python3 -m pip install -r ./requirements.txt -t site-packages
