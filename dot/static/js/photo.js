// Classe para manipulação de foto, webcam

class jsPhoto{
    constructor(options){
        // Variaveis internas ********
        this.cropper = null; // Aponta para o objeto cropper.js
        this.modal = null; // Aponta para o modal
        this.image = null; // Aponta para o img
        this.streaming = false; // Controla se webcam esta em uso
        // Configuracao ********
        this.imageSrc = options?.imageSrc || ''; // Caminho da imagem a ser pre carregada (caso exista)
        this.canUploadImage = options?.canUploadImage != undefined ? options.canUploadImage : true; // Habilita / desabilita o input file
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.cropperFixed = options?.cropperFixed || false; // Altere para true para aspectRatio: 1
        this.cropperRotateAngle = options?.cropperRotateAngle || 3; // Angulo de rotacao base para o cropper
        this.save = options?.save || this.__save; // Metodo que responde pela acao do save
        this.previewTarget = options?.previewTarget || null; // Se informado, ajusta exibicao ao fechar form
        this.inputTarget = options?.inputTarget || null; // Se informado input, ao gravar no modal, salva dataUrl imagem editada no input
        this.cropperOptions = options?.cropperOptions || this.__setDefaultCropperOptions();
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
    __setDefaultCropperOptions(){
        let opt = {viewMode: 1, autoCropArea:1, dragMode: 'move'};
        if(this.cropperShape == 'circ' || this.cropperFixed == true){
            opt['aspectRatio'] = 1;
        }
        return opt;
    }
    __createModal(){
        let modal = document.createElement('div');modal.classList = 'modal fade';modal.tabIndex = '-1';
        let dialog = document.createElement('div');dialog.classList = 'modal-dialog modal-fullscreen';
        let content = document.createElement('div');content.classList = 'modal-content';
        let header = document.createElement('div');header.classList = 'py-2 px-3 border-bottom';
        let body = document.createElement('div');body.classList = 'modal-body text-center';
        let footer = document.createElement('div');footer.classList = 'modal-footer py-2 bg-light';
        let dismiss = document.createElement('button');dismiss.classList = 'btn btn-sm btn-secondary';dismiss.setAttribute('data-bs-dismiss', 'modal');dismiss.innerHTML = 'Cancelar';
        this.saveModalBtn = document.createElement('button');this.saveModalBtn.classList = 'btn btn-sm btn-primary';this.saveModalBtn.innerHTML = 'Gravar';
        this.saveModalBtn.onclick = () => {
            if(this.inputTarget){this.__saveDataURLOnInputTarget()}
            if(this.previewTarget){this.__refreshPreview()}
            this.modal.hide();
        };
        // ------------------------------
        let img_container = document.createElement('div');
        this.image = document.createElement('img');this.image.src = this.imageSrc;this.image.style.maxWidth = '100%';
        img_container.appendChild(this.image);
        body.appendChild(img_container);
        footer.appendChild(dismiss);
        footer.appendChild(this.saveModalBtn);
        this.__createControls(header); // Adiciona os controles do componente
        content.appendChild(header);
        content.appendChild(body);
        content.appendChild(footer);
        dialog.appendChild(content);
        modal.appendChild(dialog);
        this.modal = new bootstrap.Modal(modal, {keyboard: true});
        // ------------------------------
        if(this.cropperEnable){
            modal.addEventListener('shown.bs.modal', () => this.__cropImage());
            modal.addEventListener('hidden.bs.modal', () => this.__cropDestroy());
        }
    }
    __createControls(container){
        let btnGroupFont = document.createElement('div');btnGroupFont.classList = 'btn-group';
        let btnGroupEdit = document.createElement('div');btnGroupEdit.classList = 'btn-group ms-1';
        let btnGroupSave     = document.createElement('div');btnGroupSave.classList = 'btn-group ms-1';
        if(this.canUploadImage){
            this.btnUpload = document.createElement('button');this.btnUpload.classList = 'btn btn-sm btn-outline-primary';this.btnUpload.innerHTML = '<i class="fas fa-upload"></i>';this.btnUpload.title = 'Carregar imagem';
            let input = document.createElement('input');input.type = 'file';input.accept = 'image/*';input.style.display = 'none';
            this.btnUpload.onclick = () => {input.click();};
            input.onchange = () => {
                if(input.files.lenght == 0){return false;}
                let file = input.files[0];
                let url = URL.createObjectURL(file);
                this.image.src = url;
                this.__cropDestroy();
                this.__cropImage();
            };
            btnGroupFont.appendChild(this.btnUpload);
        }
        if(this.webcamEnable){
            this.btnWebcam = document.createElement('button');this.btnWebcam.classList = 'btn btn-sm btn-outline-primary';this.btnWebcam.innerHTML = '<i class="fas fa-camera"></i>';this.btnWebcam.title = 'Webcam';
            this.btnWebcam.onclick = () => {this.__startWebCam()};
            btnGroupFont.appendChild(this.btnWebcam);
        }
        // Botoes do grupo edicao....
        this.btnZoomIn = document.createElement('button');this.btnZoomIn.classList = 'btn btn-sm btn-outline-primary';this.btnZoomIn.innerHTML = '<i class="fas fa-search-plus"></i>';this.btnZoomIn.title = 'Aumentar Zoom';
        this.btnZoomIn.onclick = () => this.cropper.zoom(0.1);
        this.btnZoomOut = document.createElement('button');this.btnZoomOut.classList = 'btn btn-sm btn-outline-primary';this.btnZoomOut.innerHTML = '<i class="fas fa-search-minus"></i>';this.btnZoomOut.title = 'Diminuir Zoom';
        this.btnZoomOut.onclick = () => this.cropper.zoom(-0.1);
        this.btnRotateLeft = document.createElement('button');this.btnRotateLeft.classList = 'btn btn-sm btn-outline-primary';this.btnRotateLeft.innerHTML = '<i class="fas fa-undo"></i>';this.btnRotateLeft.title = 'Girar para Esquerda';
        this.btnRotateLeft.onclick = () => this.cropper.rotate(this.cropperRotateAngle * -1);
        this.btnRotateRight = document.createElement('button');this.btnRotateRight.classList = 'btn btn-sm btn-outline-primary';this.btnRotateRight.innerHTML = '<i class="fas fa-redo"></i>';this.btnRotateRight.title = 'Girar para Direita';
        this.btnRotateRight.onclick = () => this.cropper.rotate(this.cropperRotateAngle);
        this.btnScaleX = document.createElement('button');this.btnScaleX.classList = 'btn btn-sm btn-outline-primary';this.btnScaleX.innerHTML = '<i class="fas fa-arrows-alt-h"></i>';this.btnScaleX.title = 'Inverter Horizontal';
        this.btnScaleX.onclick = () => this.cropper.scaleX(this.cropper.getImageData().scaleX * -1 || -1);
        this.btnScaleY = document.createElement('button');this.btnScaleY.classList = 'btn btn-sm btn-outline-primary';this.btnScaleY.innerHTML = '<i class="fas fa-arrows-alt-v px-1"></i>';this.btnScaleY.title = 'Inverter Vertical';
        this.btnScaleY.onclick = () => this.cropper.scaleY(this.cropper.getImageData().scaleY * -1 || -1);
        btnGroupEdit.appendChild(this.btnZoomIn);
        btnGroupEdit.appendChild(this.btnZoomOut);
        btnGroupEdit.appendChild(this.btnRotateLeft);
        btnGroupEdit.appendChild(this.btnRotateRight);
        btnGroupEdit.appendChild(this.btnScaleX);
        btnGroupEdit.appendChild(this.btnScaleY);
        // Botoes do grupo extra
        this.btnReset = document.createElement('button');this.btnReset.classList = 'btn btn-sm btn-outline-secondary';this.btnReset.innerHTML = '<i class="fas fa-sync"></i>';this.btnReset.title = 'Desfazer alterações';
        this.btnReset.onclick = () => this.cropper.reset();
        btnGroupSave.appendChild(this.btnReset);
        
        container.appendChild(btnGroupFont);
        container.appendChild(btnGroupEdit);
        container.appendChild(btnGroupSave);
    }
    __cropImage(){this.cropper = new Cropper(this.image, this.cropperOptions);}
    __cropDestroy(){this.cropper.destroy();}
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
    __refreshPreview(){
        this.previewTarget.src = this.cropper.getCroppedCanvas().toDataURL();
    }
    __saveDataURLOnInputTarget(options){
        let croppedCanvas = this.cropper.getCroppedCanvas();
        if(this.cropperShape == 'circ'){croppedCanvas = this.__getRoundedCanvas(croppedCanvas);}
        let data = croppedCanvas.toDataURL();
        this.inputTarget.value = data;
    }
    __startWebCam(){
        this.__cropDestroy(); // Destroy o cropper
        this.image.classList.add('d-none'); // Oculta a imagem
        // Definicoes para o canvas de captura de video
        let videoW = '550';
        let videoH = '550';
        this.video = document.createElement('video');
        this.video.width = videoW;
        this.video.height = videoH;
        // this.video.style.backgroundColor = '#CCC';
        this.image.after(this.video);
        // -------------------
        navigator.mediaDevices.getUserMedia({video: true, audio: false})
        .then(function(stream){this.video.srcObject = stream;this.video.play();})
        .catch(function(e){console.log(e);});

        this.video.addEventListener('canplay', function(ev){
            if (!this.streaming) {
                // height = video.videoHeight / (video.videoWidth/width);  
                // if (isNaN(height)) {height = width / (4/3);}
                // video.setAttribute('width', width);
                // video.setAttribute('height', height);
                // canvas.setAttribute('width', width);
                // canvas.setAttribute('height', height);
                this.streaming = true;
            }
        }, false);
        // clearphoto();
    }
    modalToogle(show=true){}
}