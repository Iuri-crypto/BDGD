import openai


def inicializar_openai():
    """Inicializa a configuração da API OpenAI."""
    # Certifique-se de ter configurado sua chave de API corretamente.
    openai.api_key = "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"  # Substitua com a sua chave de API OpenAI


def gerar_texto(prompt, max_tokens=1500):
    """
    Gera um texto com base no prompt fornecido usando o modelo da OpenAI.

    Args:
        prompt (str): O prompt de entrada para o modelo de linguagem.
        max_tokens (int): O número máximo de tokens para gerar no texto.

    Returns:
        str: O texto gerado pelo modelo.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro ao gerar texto: {e}")
        return None


def criar_tcc(tema):
    """
    Cria o conteúdo de um TCC com base no tema fornecido.

    Args:
        tema (str): O tema do TCC.

    Returns:
        str: O texto completo do TCC.
    """
    prompt = f"Escreva um TCC sobre o tema: {tema}. Inclua uma introdução, desenvolvimento e conclusão."
    texto = gerar_texto(prompt)
    if texto:
        return texto
    else:
        return "Não foi possível gerar o TCC. Por favor, tente novamente."


def main():
    """
    Função principal que coleta o tema do TCC e gera o conteúdo.
    """
    inicializar_openai()
    tema = input("Digite o tema do seu TCC: ")
    tcc_completo = criar_tcc(tema)
    print("Seu TCC foi gerado:")
    print(tcc_completo)


if __name__ == "__main__":
    main()
