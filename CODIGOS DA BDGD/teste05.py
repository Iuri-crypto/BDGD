from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import webbrowser


def inicializar_modelo():
    """
    Inicializa o modelo e o tokenizer do GPT-2.

    Returns:
        model (GPT2LMHeadModel): O modelo GPT-2 carregado.
        tokenizer (GPT2Tokenizer): O tokenizer GPT-2 carregado.
    """
    model_name = "gpt2-medium"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    return model, tokenizer


def gerar_texto(prompt, model, tokenizer, max_length=500):
    """
    Gera um texto com base no prompt fornecido usando o modelo GPT-2.

    Args:
        prompt (str): O prompt de entrada para o modelo de linguagem.
        model (GPT2LMHeadModel): O modelo GPT-2 carregado.
        tokenizer (GPT2Tokenizer): O tokenizer GPT-2 carregado.
        max_length (int): O número máximo de tokens para gerar no texto.

    Returns:
        str: O texto gerado pelo modelo.
    """
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        early_stopping=True,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def criar_tcc(tema):
    """
    Cria o conteúdo de um TCC com base no tema fornecido.

    Args:
        tema (str): O tema do TCC.

    Returns:
        str: O texto completo do TCC.
    """
    prompt = f"Escreva um TCC sobre o tema: {tema}. Inclua uma introdução, desenvolvimento e conclusão. Detalhe os seguintes pontos: impacto histórico, estado atual e perspectivas futuras."
    model, tokenizer = inicializar_modelo()
    texto = gerar_texto(prompt, model, tokenizer)
    return texto


def salvar_em_pdf(titulo, texto, arquivo_pdf):
    """
    Salva o conteúdo em um arquivo PDF formatado.

    Args:
        titulo (str): O título do TCC.
        texto (str): O conteúdo do TCC.
        arquivo_pdf (str): O caminho para salvar o PDF.
    """
    c = canvas.Canvas(arquivo_pdf, pagesize=letter)
    width, height = letter

    # Adiciona título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, titulo)

    # Adiciona texto
    c.setFont("Helvetica", 12)
    text = c.beginText(72, height - 100)
    text.setFont("Helvetica", 12)
    text.setTextOrigin(72, height - 100)
    text.setWordSpace(0.2)
    text.setLineSpacing(14)
    text.textLines(texto)
    c.drawText(text)

    # Finaliza o PDF
    c.showPage()
    c.save()


def abrir_pdf(arquivo_pdf):
    """
    Abre o arquivo PDF gerado.

    Args:
        arquivo_pdf (str): O caminho do arquivo PDF.
    """
    if os.name == 'nt':  # Para Windows
        os.startfile(arquivo_pdf)
    elif os.name == 'posix':  # Para Linux e MacOS
        webbrowser.open(arquivo_pdf)


def main():
    """
    Função principal que coleta o tema do TCC, gera o conteúdo e salva em PDF.
    """
    tema = input("Digite o tema do seu TCC: ")
    tcc_completo = criar_tcc(tema)
    titulo = f"TCC: {tema.capitalize()}"
    arquivo_pdf = "TCC_Gerado.pdf"
    salvar_em_pdf(titulo, tcc_completo, arquivo_pdf)
    abrir_pdf(arquivo_pdf)
    print("Seu TCC foi gerado e salvo como PDF.")


if __name__ == "__main__":
    main()
