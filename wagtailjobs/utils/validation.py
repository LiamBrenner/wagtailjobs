from django.contrib import messages


def validation(request, job, is_sending_email):
    if is_sending_email:
        if not job.email:
            messages.error(request, ('You cannot email an job without an email to send it to. Please save the job without emailing it!'))
            return False

    return True
