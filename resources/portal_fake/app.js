const paginaLogin = document.querySelector("#pagina_login");
const paginaFormulario = document.querySelector("#pagina_formulario");
const formLogin = document.querySelector("#form_login");
const formLote = document.querySelector("#form_lote");
const mensagemLogin = document.querySelector("#mensagem_login");
const mensagemSucesso = document.querySelector("#mensagem_sucesso");

formLogin.addEventListener("submit", (event) => {
  event.preventDefault();

  const usuario = document.querySelector("#user-name").value;
  const senha = document.querySelector("#password").value;

  if (!usuario.trim() || !senha.trim()) {
    mensagemLogin.textContent = "Usuário ou senha inválidos.";
    return;
  }

  paginaLogin.hidden = true;
  paginaFormulario.hidden = false;
  window.location.hash = "cadastro";
});

formLote.addEventListener("submit", (event) => {
  event.preventDefault();

  const cadastro = {
    numero_lote: document.querySelector("#numero_lote").value,
    produto: document.querySelector("#produto").value,
    status: document.querySelector("#status").value,
  };

  localStorage.setItem("ultimo_lote", JSON.stringify(cadastro));
  mensagemSucesso.hidden = false;
});
