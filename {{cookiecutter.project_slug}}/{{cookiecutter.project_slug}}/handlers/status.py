"""Status checks."""


async def status(request):  # noqa
    """Return status.
    ---

    tags: [health]
    description: Application status
    responses:
      200:
        description: OK
      400:
        description: Validation error
    """
    return {'status': 0}
