// Classe para manipulação de foto, webcam

class jsPhoto{
    constructor(options){
        // Variaveis internas ********
        this.cropper = null; // Aponta para o objeto cropper.js
        this.modal = null; // Aponta para o modal
        this.image = null; // Aponta para o img
        // Configuracao ********
        this.imageSrc = options?.imageSrc || ''; // Caminho da imagem a ser pre carregada (caso exista)
        this.canUploadImage = options?.canUploadImage != undefined ? options.canUploadImage : true; // Habilita / desabilita o input file
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.save = options?.save || this.__save; // Metodo que responde pela acao do save
        this.inputTarget = options?.inputTarget || null; // Se informado input, ao gravar no modal, salva imagem editada no input
        this.cropperOptions = options?.cropperOptions || {autoCropArea: 0.5}; // Opções da instancia cropper.js
        // Estilizacao ********

        this.__configureCssClass()
        this.__createModal();
    }
    __configureCssClass(){
        if(this.cropperShape == 'default'){return false;}
        let style = document.createElement('style');
        if(this.cropperShape == 'circ'){style.innerHTML = '.cropper-view-box,.cropper-face{border-radius: 50%;}';}
        document.getElementsByTagName('head')[0].appendChild(style);
    }
    __createModal(){
        let modal = document.createElement('div');modal.classList = 'modal fade';modal.tabIndex = '-1';
        let dialog = document.createElement('div');dialog.classList = 'modal-dialog modal-fullscreen';
        let content = document.createElement('div');content.classList = 'modal-content';
        let header = document.createElement('div');header.classList = 'py-2 px-3 border-bottom';
        let body = document.createElement('div');body.classList = 'modal-body text-center';
        let footer = document.createElement('div');footer.classList = 'modal-footer py-2 bg-light';
        let dismiss = document.createElement('button');dismiss.classList = 'btn btn-sm btn-secondary';dismiss.setAttribute('data-bs-dismiss', 'modal');dismiss.innerHTML = 'Cancelar';
        // ------------------------------
        let img_container = document.createElement('div');
        this.image = document.createElement('img');this.image.src = this.imageSrc;this.image.style.maxWidth = '100%';
        img_container.appendChild(this.image);
        body.appendChild(img_container);
        footer.appendChild(dismiss);
        this.__createControls(header); // Adiciona os controles do componente
        content.appendChild(header);
        content.appendChild(body);
        content.appendChild(footer);
        dialog.appendChild(content);
        modal.appendChild(dialog);
        this.modal = new bootstrap.Modal(modal, {keyboard: true});
        // ------------------------------
        if(this.cropperEnable){
            let cropBoxData;
            let canvasData;
            let self = this;
            modal.addEventListener('shown.bs.modal', function(){
                this.cropper = new Cropper(self.image, {
                    aspectRatio: 1,
                    viewMode: 1,
                    ready: function(){this.cropper.setCropBoxData(cropBoxData).setCanvasData(canvasData);}
                });
            });
            modal.addEventListener('hidden.bs.modal', function(){
                cropBoxData = this.cropper.getCropBoxData();
                canvasData = this.cropper.getCanvasData();
                self.cropper.destroy();
            });
            
        }
    }
    __createControls(container){
        let btnGroup = document.createElement('div');btnGroup.classList = 'btn-group';
        if(this.canUploadImage){
            this.btnUpload = document.createElement('button');this.btnUpload.classList = 'btn btn-sm btn-outline-primary';this.btnUpload.innerHTML = '<i class="fas fa-upload"></i>';
            let input = document.createElement('input');input.type = 'file';input.accept = 'image/*';input.style.display = 'none';
            let self = this;
            this.btnUpload.onclick = () => {
                input.click();
            };
            input.onchange = () => {
                if(input.files.lenght == 0){return false;}
                let file = input.files[0];
                let url = URL.createObjectURL(file);
                this.image.src = url;
            };
            btnGroup.appendChild(this.btnUpload);
        }
        container.appendChild(btnGroup);
    }
    __save(){}
    __getRoundedCanvas(source){
        let canvas = document.createElement('canvas');
        let context = canvas.getContext('2d');
        let width = source.width;
        let height = source.height;
        
        canvas.width = width;
        canvas.height = height;
        context.imageSmoothingEnabled = true;
        context.drawImage(source, 0, 0, width, height);
        context.globalCompositeOperation = 'destination-in';
        context.beginPath();
        context.arc(width / 2, height / 2, Math.min(width, height) / 2, 0, 2 * Math.PI, true);
        context.fill();
        return canvas;
    }
    modalToogle(show=true){}
}