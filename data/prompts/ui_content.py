from src.external_links import (
    INSTAGRAM_VOX,
    INSTAGRAM_MARIELLE,
    FORM_AVALIACAO,
    LINKTREE_VOX,
    LINKEDIN_VOX,
    EMAIL_CONTATO,
    GITHUB,
    HUGGING_FACE_SPACE,
    TERMS_OF_USE,
    POLICY_PRIVACY,
)
from src.utils import git_version

SAUDACAO = """
Olá! Sou o Vox AI, seu assistente de apoio e informação sobre a comunidade LGBTQIA+.
Você pode me perguntar sobre:
- Saúde e prevenção (como PrEP, PEP, ISTs ou saúde mental)
- Locais de acolhimento e serviços para pessoas LGBTQIA+
- Direitos, cultura e outras dúvidas sobre nossa comunidade
 
Como posso te ajudar agora?
"""

SIDEBAR_BODY = f"""
<div style="display: flex; flex-direction: column; margin-bottom: 1em; justify-content: space-between;">
    <div>
        <div class="vox-sidebar-title">Sobre o Vox</div>
        <div class="vox-sidebar-section">
            <b>Vox AI</b> é um assistente de apoio e informação <b>LGBTQIA+</b>. Aqui você encontra acolhimento,
            informações e recursos confiáveis.<br>
        </div>
        <br>
        <div style="margin-bottom: 1.5em;">
            <div style="font-size: 0.85em; color: #888; margin-bottom: 0.5em; font-weight: bold;">Siga nosso trabalho
            </div>
            <ul class="vox-sidebar-links">
                <li>
                    <a href="{INSTAGRAM_VOX}" target="_blank" class="link-insta">
                        <img src="https://img.icons8.com/?size=100&id=Xy10Jcu1L2Su&format=png" alt="Instagram"
                            style="height:1.3em; vertical-align:middle; margin-right:5px;" />
                        @projetovoxai
                    </a>
                </li>
                <li>
                    <a href="{INSTAGRAM_MARIELLE}" target="_blank"
                        class="link-casa-marielle">
                        <img src="https://img.icons8.com/?size=100&id=Xy10Jcu1L2Su&format=png" alt="Instagram"
                            style="height:1.3em; vertical-align:middle; margin-right:5px;" />
                        @casamariellefrancobr
                    </a>
                </li>
                <li>
                    <a href="{FORM_AVALIACAO}" target="_blank" title="Avaliar o Vox">
                        <img src="https://img.icons8.com/?size=100&id=19417&format=png&color=000000" alt="Avaliar"
                            style="height:1.3em; vertical-align:middle; margin-right:5px;" />
                        Avalie o Vox
                    </a>
                </li>
            </ul>
        </div>
        <div style="font-size: 0.85em; color: #888; margin-bottom: 0.8em; font-weight: bold;">Conecte-se</div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <a href="{LINKTREE_VOX}" target="_blank" title="Linktree (Todos os nossos links)">
                <img src="https://img.icons8.com/?size=100&id=GfTOMrwiax2M&format=png&color=000000 alt="Linktree"
                    style="height: 32px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'"
                    onmouseout="this.style.transform='scale(1)'" />
            </a>
            <a href="{LINKEDIN_VOX}" target="_blank" title="LinkedIn">
                <img src="https://img.icons8.com/?size=100&id=13930&format=png&color=000000" alt="LinkedIn (@projetovox)"
                    style="height: 32px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'"
                    onmouseout="this.style.transform='scale(1)'" />
            </a>
            <a href="{EMAIL_CONTATO}" target="_blank" title="Enviar E-mail">
                <img src="https://img.icons8.com/?size=100&id=ho8QlOYvMuG3&format=png&color=000000" alt="Email"
                    style="height: 32px;transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.2)'"
                    onmouseout="this.style.transform='scale(1)'" />
            </a>
        </div>
    </div>
    <hr style="margin: 1em 0;">
"""
SIDEBAR_FOOTER = f"""
    <div>
        <div>
            <div style="text-align: center;">
                <a href="{GITHUB}" target="_blank" title="Ver código fonte" style="text-decoration: none;">
                    <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg" alt="GitHub"
                        style="height: 2em; filter: invert(1) opacity(0.6); transition: opacity 0.2s;" />
                </a>
                <a href="{HUGGING_FACE_SPACE}" target="_blank" title="Hugging Face Space" style="text-decoration: none;">
                    <img src="https://img.icons8.com/?size=100&id=sop9ROXku5bb&format=png" alt="Hugging Face"
                        style="height: 32px; transition: transform 0.2s;"
                        onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'" />
                </a>
            </div>
            <div class="footer-section" style="text-align:center; margin-top: 1em;">
                <a href="{TERMS_OF_USE}" target="_blank" style="text-decoration: none;"
                    class="legal-link">Termos de Uso</a></br>
                <a href="{POLICY_PRIVACY}" target="_blank" style="text-decoration: none;"
                    class="legal-link">Política de Privacidade</a>
            </div>
            <div class="copyright" style="text-align:center; color:#666; font-size:0.8em; margin-top:1.5em;">
                Copyright © 2025 Vox AI
            </div>
        </div>
        <div style='color: #88888888; text-align: center; margin: auto; font-size: 0.9em;'>
            {git_version()}
        </div>
    </div>
"""
