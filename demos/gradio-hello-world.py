# https://www.gradio.app/docs/interface
# https://www.gradio.app/custom-components/gallery

import gradio as gr

def greet(name):
    return "Hello " + name + "!"

app = gr.Interface(fn=greet, inputs="text", outputs="text")
# share=True créerait un lien public via les serveurs de Gradio : désactivé par défaut
app.launch(server_name="0.0.0.0", server_port=7860)
