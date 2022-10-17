// Classe para manipulação de foto, webcam

class jsPhoto{
    constructor(options){
        // Variaveis internas ********
        this.cropper = null; // Aponta para o objeto cropper.js
        this.modal = null; // Aponta para o modal
        this.image = null; // Aponta para o img
        this.viewMode = 'default'; // Verifica perfil de exibicao atual
        this.streaming = false; // Controla se webcam esta em uso
        // Configuracao ********
        this.imageSrc = options?.imageSrc || ''; // Caminho da imagem a ser pre carregada (caso exista)
        this.canUploadImage = options?.canUploadImage != undefined ? options.canUploadImage : true; // Habilita / desabilita o input file
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.cropperFixed = options?.cropperFixed || false; // Altere para true para aspectRatio: 1
        this.cropperRotateAngle = options?.cropperRotateAngle || 3; // Angulo de rotacao base para o cropper
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
        if(this.cropperShape == 'circ' || this.cropperFixed == true){opt['aspectRatio'] = 1;}
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
        dismiss.onclick = () => {
            if(this.bkpImage != undefined){this.image.src = this.bkpImage;this.bkpImage = undefined;} // Restaura backup da imagem (caso exista)
            if(this.viewMode == 'webcam'){this.__endWebCam();}
        }
        this.saveModalBtn = document.createElement('button');this.saveModalBtn.classList = 'btn btn-sm btn-primary';this.saveModalBtn.innerHTML = 'Gravar';
        this.saveModalBtn.onclick = () => {
            if(this.viewMode == 'webcam'){
                this.__endWebCam();
                let self = this;
                this.image.addEventListener('ready', function jsPhotoModalHandler() {
                    self.image.removeEventListener('ready', jsPhotoModalHandler);
                    if(self.inputTarget){self.__saveDataURLOnInputTarget()}
                    if(self.previewTarget){self.__refreshPreview()}
                    self.modal.hide();
                });
            }
            else{
                if(this.inputTarget){this.__saveDataURLOnInputTarget()}
                if(this.previewTarget){this.__refreshPreview()}
                this.modal.hide();
            }
        };
        // ------------------------------
        this.img_container = document.createElement('div');
        this.image = document.createElement('img');this.image.src = this.imageSrc;this.image.style.maxWidth = '100%';
        this.img_container.appendChild(this.image);
        body.appendChild(this.img_container);
        // Definicoes para o canvas de captura de video
        if(this.webcamEnable){
            let videoW = Math.min(__sw, 650);
            let videoH = videoW / (4/3);
            this.video = document.createElement('video');this.video.classList = 'border rounded d-none';
            this.video.width = videoW;
            this.video.height = videoH;
            this.video.innerHTML = 'Seu navegador nao da suporte a este recurso';
            this.videoCaptured = document.createElement('canvas');this.videoCaptured.classList = 'border rounded d-none'; // Inicia oculto
            let gap = 10;
            this.videoCaptured.width = videoW - gap;
            this.videoCaptured.height = videoH - gap;
            body.appendChild(this.video);
            body.appendChild(this.videoCaptured);
        }
        // -------------------
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
        this.btnGroupFont = document.createElement('div');this.btnGroupFont.classList = 'btn-group';
        this.btnGroupEdit = document.createElement('div');this.btnGroupEdit.classList = 'btn-group ms-1';
        this.btnGroupStreaming = document.createElement('div');this.btnGroupStreaming.classList = 'btn-group ms-2 d-none';
        this.btnGroupSave = document.createElement('div');this.btnGroupSave.classList = 'btn-group ms-1';
        if(this.canUploadImage){
            this.btnUpload = document.createElement('button');this.btnUpload.classList = 'btn btn-sm btn-outline-primary';this.btnUpload.innerHTML = '<i class="fas fa-upload"></i>';this.btnUpload.title = 'Carregar imagem';
            this.jsPhotoInput = document.createElement('input');this.jsPhotoInput.type = 'file';this.jsPhotoInput.accept = 'image/*';this.jsPhotoInput.style.display = 'none';
            this.btnUpload.onclick = () => {this.jsPhotoInput.click();};
            this.jsPhotoInput.onchange = () => {
                if(this.jsPhotoInput.files.lenght == 0){return false;}
                let file = this.jsPhotoInput.files[0];
                let url = URL.createObjectURL(file);
                this.image.src = url;
                if(this.cropperEnable){
                    this.__cropDestroy();
                    this.__cropImage();
                }
            };
            this.btnGroupFont.appendChild(this.btnUpload);
        }
        if(this.webcamEnable){
            this.btnWebcam = document.createElement('button');this.btnWebcam.classList = 'btn btn-sm btn-outline-primary';this.btnWebcam.innerHTML = '<i class="fas fa-camera"></i>';this.btnWebcam.title = 'Webcam';
            this.btnWebcam.onclick = () => {
                if(this.cropperEnable){this.__cropDestroy();}
                this.img_container.classList.add('d-none');
                this.__startWebCam();
                this.viewMode = 'webcam';
            };
            this.btnGroupFont.appendChild(this.btnWebcam);
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
        this.btnGroupEdit.appendChild(this.btnZoomIn);
        this.btnGroupEdit.appendChild(this.btnZoomOut);
        this.btnGroupEdit.appendChild(this.btnRotateLeft);
        this.btnGroupEdit.appendChild(this.btnRotateRight);
        this.btnGroupEdit.appendChild(this.btnScaleX);
        this.btnGroupEdit.appendChild(this.btnScaleY);
        // Botoes do grupo streaming
        this.btnStreamingToogle = document.createElement('button');this.btnStreamingToogle.classList = 'btn btn-sm btn-outline-secondary';this.btnStreamingToogle.innerHTML = '<i class="fas fa-stop"></i>';this.btnStreamingToogle.title = 'Inicia / para webcam';
        this.btnStreamingToogle.onclick = () => {
            if(this.streaming){this.__stopWebCam();}
            else{this.__startWebCam();}
        };
        this.btnStreamingCapture = document.createElement('button');this.btnStreamingCapture.classList = 'btn btn-sm btn-outline-secondary';this.btnStreamingCapture.innerHTML = '<i class="fas fa-clone fa-fw"></i>Capturar';this.btnStreamingCapture.title = 'Capturar imagem';
        this.btnStreamingCapture.onclick = () => {this.__webcamCapture()};
        this.btnStreamingEnd = document.createElement('button');this.btnStreamingEnd.classList = 'btn btn-sm btn-secondary';this.btnStreamingEnd.innerHTML = '<i class="fas fa-crop px-1"></i>';this.btnStreamingEnd.title = 'Editar imagem';
        this.btnStreamingEnd.onclick = () => {this.__endWebCam()};
        this.btnGroupStreaming.appendChild(this.btnStreamingToogle)
        this.btnGroupStreaming.appendChild(this.btnStreamingCapture)
        this.btnGroupStreaming.appendChild(this.btnStreamingEnd)
        // Botoes do grupo extra
        this.btnReset = document.createElement('button');this.btnReset.classList = 'btn btn-sm btn-outline-secondary';this.btnReset.innerHTML = '<i class="fas fa-sync"></i>';this.btnReset.title = 'Desfazer alterações';
        this.btnReset.onclick = () => this.cropper.reset();
        this.btnGroupSave.appendChild(this.btnReset);
        
        container.appendChild(this.btnGroupFont);
        container.appendChild(this.btnGroupEdit);
        container.appendChild(this.btnGroupStreaming);
        container.appendChild(this.btnGroupSave);
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
        if(this.cropperEnable){this.previewTarget.src = this.cropper.getCroppedCanvas().toDataURL();}
        else{this.previewTarget.src = this.image.src}
    }
    __saveDataURLOnInputTarget(options){
        // 1) Verifica se cropper esta ativo, se sim gera o dataUtl baseado na area do cropper
        // 2) Caso nao, avalia se foi carregado algum arquivo do disco, se sim le arquivo e gera dataUrl
        // 3) Caso nao, gera dataUtl do objeto this.image
        if(this.cropperEnable){
            let croppedCanvas = this.cropper.getCroppedCanvas();
            if(this.cropperShape == 'circ'){croppedCanvas = this.__getRoundedCanvas(croppedCanvas);}
            let data = croppedCanvas.toDataURL();
            this.inputTarget.value = data;
        }
        else{
            if(this.jsPhotoInput.files.length > 0){
                let reader = new FileReader();
                reader.onloadend = () => {this.inputTarget.value = reader.result;};
                reader.readAsDataURL(this.jsPhotoInput.files[0]);
                this.inputTarget.value = data;
            }
            else{this.inputTarget.value = this.image.src;}
        }
    }
    __startWebCam(){
        // Navegador vai retornar undefined para navigator.mediaDevices se conexao nao for segura (https)
        // neste caso exibe mensagem de alerta e retorna false
        if(!navigator.mediaDevices){
            this.modal.hide();
            dotAlert('warning', '<b>Atenção:</b> <code>navigator.mediaDevices</code> requer conexão segura (https), entre em contato com o administrador.', false);
            return false;
        }
        this.videoCaptured.classList.add('d-none'); // Oculta a captura (caso exibido)
        this.video.classList.remove('d-none'); // Exibe o video
        let self = this;
        navigator.mediaDevices.getUserMedia({video: true, audio: false})
        .then(function(stream){self.video.srcObject = stream;self.video.play();})
        .catch(function(e){console.log(e)});

        this.btnGroupFont.classList.add('d-none');
        this.btnGroupEdit.classList.add('d-none');
        this.btnGroupSave.classList.add('d-none');
        this.btnGroupStreaming.classList.remove('d-none');
        this.streaming = true;
        this.btnStreamingToogle.innerHTML = '<i class="fas fa-stop fa-fw me-0"></i>';
    }
    __stopWebCam(){ // Finaliza gravacao
        if(!this.streaming){return false;}
        let mediaStream = this.video.srcObject;
        let tracks = mediaStream.getTracks();
        tracks[0].stop();
        this.streaming = false;
        this.video.classList.add('d-none');
        this.videoCaptured.classList.remove('d-none');
        this.btnStreamingToogle.innerHTML = '<i class="fas fa-play fa-fw me-0"></i>';
    }
    __webcamCapture(){ // Captura imagem do canvas e salva em this.image
        if(!this.streaming){return false;}
        this.bkpImage = this.image.src;
        let context = this.videoCaptured.getContext('2d');
        context.drawImage(this.video, 0, 0, this.video.videoWidth, this.video.videoHeight);
        let data = this.videoCaptured.toDataURL('image/png');
        this.videoCaptured.src = data; // Atualiza o preview do video
        this.image.src = data; // Atualiza a imagem principal
        this.__stopWebCam();
    }
    __endWebCam(){ // Finaliza as operacoes com captura da webcam
        if(this.streaming){this.__stopWebCam();}
        this.video.classList.add('d-none');
        this.videoCaptured.classList.add('d-none');
        this.btnGroupStreaming.classList.add('d-none');
        this.img_container.classList.remove('d-none');
        this.btnGroupFont.classList.remove('d-none');
        this.btnGroupEdit.classList.remove('d-none');
        this.btnGroupSave.classList.remove('d-none');
        if(this.cropperEnable){this.__cropImage()}
        this.viewMode = 'default';
    }
}