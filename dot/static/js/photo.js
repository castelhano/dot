// Classe para manipulação de foto, webcam

class jsPhoto{
    constructor(options){
        // Variaveis internas ********
        this.cropper = null; // Aponta para o objeto cropper.js
        this.modal = null; // Aponta para o modal
        // Configuracao ********
        this.image = options?.image || null; // Imagem original
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.save = options?.save || this.__save; // Metodo que responde pela acao do save
        this.inputTarget = options?.inputTarget || null; // Se informado input, ao gravar no modal, salva imagem editada no input
        this.cropperOptions = options?.cropperOptions || {}; // Opções da instancia cropper.js
        // Estilizacao ********
    }
    __createModal(){}
    __createControls(){}
    __save(){}
    modalToogle(show=true){}
}