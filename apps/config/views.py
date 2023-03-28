import markdown
import sys
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# from config.models import Site
# from notification.utils import create_email
# from notification.utils import notify_error

from apps.utils.utils import default_render_template_email, html_response


# HTTP Error 400
def bad_request(request, exception):
	return html_response(request, 'errors/400.html', 400)


# HTTP Error 403
def permission_denied(request, exception):
	return html_response(request, 'errors/403.html', 403)


# HTTP Error 404
def page_not_found(request, exception):
	return html_response(request, 'errors/404.html', 404)


# HTTP Error 500
def server_error(request):
	return html_response(request, 'errors/500.html', 500)


def home(request):
    return redirect('/admin/')


def login_view(request):
	logout(request)
	username = password = ''
	has_next = request.GET["next"] if "next" in request.GET else ""

	action_url = request.path_info
	if has_next:
		action_url += '?next=' + has_next

	context = {
		'assets_url': settings.MEDIA_URL,
		'app_title': "Realiza Digital | Login",
		'action_url': action_url,
		'form': None,
		'post_msg': ""
	}

	if request.POST:
		form = AuthenticationForm(request, data=request.POST)
		context['form'] = form

		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)

			if user is not None:
				if user.is_active and user.is_staff:
					login(request, user)
					return HttpResponseRedirect('/admin/' if len(has_next) == 0 else has_next)
				elif not user.is_active and user.is_staff:
					context['post_msg'] = 'Por favor, ative a sua conta. Para maiores informações entre em contato com o Administrador.'
				elif not user.is_staff:
					context['post_msg'] = 'O usuário ainda não é um membro da equipe. Entre em contato com o Administrador.'
	else:
		form = AuthenticationForm(request)
		context['form'] = form

	return html_response(request, '/accounts/login.html', 200, context)


def password_reset(request):
	context = {
		'assets_url': settings.MEDIA_URL,
		'app_title': "Realiza Digital | Nova senha",
		'action_url': "/accounts/password-reset/",
		'post_msg': None,
		'form': None,
		'error': None
	}

	if request.method == "POST":
		form = PasswordResetForm(request.POST)

		if form.is_valid():
			email = form.cleaned_data['email'].lower()

			try:
				user = User.objects.get(email__iexact=email)
				subject = "Solicitação de redefinição de senha"
				token = default_token_generator.make_token(user)
				email_template_name = settings.BASE_DIR + '/templates/email/password_reset_email'

				url_admin = site.url_admin.replace("/admin", "")
				if url_admin[-1] == "/":
					url_admin = url_admin[0:-1]

				email_link = "{}/accounts/password-reset-confirm/{}/{}".format(url_admin, urlsafe_base64_encode(force_bytes(user.id)), token)
				email_args = {
					'email': user.email,
					'site_name': settings.SITE_NAME,
					'user': user,
					'email_link': email_link,
				}

				email_content, _ = default_render_template_email(email_template_name, email_args, site)

				error = "Ocorreu um erro interno. Por favor tente novamente em alguns instantes."

				try:
					internal_subject = "Pedido para criar nova senha"
					result = create_email(user.email, subject, email_content, internal_subject, "user.id:{}-uuid:{}".format(user.id, uuid4()))
					if result is None:
						raise Exception("Erro crítico! Objeto notification.Email não pode ser criado!")
					else:
						context['post_msg'] = "Se o email estiver associado a uma conta de usuário, você receberá um email com instruções para criar uma nova senha."
				except Exception as e:
					_, _, exc_tb = sys.exc_info()
					notify_error(__file__, exc_tb.tb_lineno, e)

					context['error'] = error
			except Exception as e2:
				_, _, exc_tb = sys.exc_info()
				notify_error(__file__, exc_tb.tb_lineno, e2)

				context['error'] = True
				context['post_msg'] = "Usuário não encontrado!<br>Por favor, revise o email e tente novamente."
		else:
			context['error'] = True
			context['post_msg'] = "Parâmetros inválidos! Por favor, tente novamente."
	else:
		form = PasswordResetForm()

	context['form'] = form

	return html_response(request, 'accounts/password_reset.html', 200, context)


class PasswordResetConfirmViewCustom(auth_views.PasswordResetConfirmView):
	post_reset_login = True

	def get_context_data(self, **kwargs):
		context = super(PasswordResetConfirmViewCustom, self).get_context_data(**kwargs)
		context['validlink'] = self.validlink
		context['app_title'] = settings.SITE_NAME + " | Nova senha"
		context['assets_url'] = settings.MEDIA_URL
		context['user_name'] = self.user
		context['is_valid_link'] = self.validlink

		return context


class PasswordResetCompleteViewCustom(auth_views.PasswordResetCompleteView):
	template_name = "registration/password_reset_complete.html"
	title = "Atualização de senha finalizada"

	def get_context_data(self, **kwargs):
		context = super(PasswordResetCompleteViewCustom, self).get_context_data(**kwargs)
		context['app_title'] = settings.SITE_NAME + " | Nova senha"
		context['assets_url'] = settings.MEDIA_URL
		return context
