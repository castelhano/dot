/*
* jsPhoto   Implementa componente para importacao imagens do disco, ou webcam
*           implementa (caso habilitado) componente cropper.js para manipulacao basica da imagem
*
* @version  1.01
* @since    18/10/2022
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com}
* @depend   cropper.js [https://fengyuanchen.github.io/cropperjs/][https://github.com/fengyuanchen/cropperjs]
* @depend   boostrap 5.2.0, fontawesome 5.15.4, dot.js
*/
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
        this.inputTarget = options?.inputTarget || null; // Se informado input, ao gravar no modal, salva dataUrl imagem editada no input
        this.previewTarget = options?.previewTarget || null; // Se informado, ajusta exibicao ao fechar form
        this.canUploadImage = options?.canUploadImage != undefined ? options.canUploadImage : true; // Habilita / desabilita o input file
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.facingMode = options?.facingMode || 'environment'; // Armazena camera default/ativa
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.cropperFixed = options?.cropperFixed || false; // Altere para true para aspectRatio: 1
        this.cropperRotateAngle = options?.cropperRotateAngle || 3; // Angulo de rotacao base para o cropper
        this.cropperOptions = options?.cropperOptions || this.__setDefaultCropperOptions();

        this.__configureCssClass()
        this.__createModal();
    }
    __configureCssClass(){
        // if(this.cropperShape == 'default'){return false;}
        let style = document.createElement('style');
        if(this.cropperShape == 'circ'){style.innerHTML = '.cropper-view-box,.cropper-face{border-radius: 50%;}';}
        if(__ss == 'sm'){style.innerHTML += '.jsPhotoBtnCapture{position:fixed;bottom:90px;left:50%;margin-left:-30px;border:1px solid #CCC;border-radius: 50px;padding: 15px 20px;font-size: 1.6rem;color: #6c757d;}';}
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
        this.modalDismiss = document.createElement('button');this.modalDismiss.classList = 'btn btn-sm btn-secondary';this.modalDismiss.setAttribute('data-bs-dismiss', 'modal');this.modalDismiss.innerHTML = 'Cancelar';
        let self = this;
        modal.addEventListener('hide.bs.modal', function(e){
            if(self.viewMode == 'webcam'){e.preventDefault();return false;} // Se estiver gravando pela webcam, desativa o fechamento do modal
            if(this.bkpImage != undefined){this.image.src = this.bkpImage;this.bkpImage = undefined;} // Restaura backup da imagem (caso exista)
            if(this.viewMode == 'webcam'){this.__endWebCam();}
        });
        this.saveModalBtn = document.createElement('button');this.saveModalBtn.classList = 'btn btn-sm btn-primary';this.saveModalBtn.innerHTML = 'Gravar';
        this.saveModalBtn.onclick = () => {
            if(this.viewMode == 'webcam'){this.__endWebCam();}
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
            let gap = 32
            let videoW = Math.min(__sw, 650) - gap;
            let videoH = videoW / (4/3);
            this.video = document.createElement('video');this.video.classList = 'rounded d-none';
            this.video.width = videoW;
            this.video.height = videoH;
            this.video.innerHTML = 'Seu navegador nao da suporte a este recurso';
            this.canvas = document.createElement('canvas');this.canvas.classList = 'rounded d-none m-0'; // Inicia oculto
            body.appendChild(this.video);
            body.appendChild(this.canvas);
        }
        // -------------------
        footer.appendChild(this.modalDismiss);
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
        if(this.cropperEnable){
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
            // Botoes do grupo extra
            this.btnReset = document.createElement('button');this.btnReset.classList = 'btn btn-sm btn-outline-secondary';this.btnReset.innerHTML = '<i class="fas fa-sync"></i>';this.btnReset.title = 'Desfazer alterações';
            this.btnReset.onclick = () => this.cropper.reset();
            this.btnGroupSave.appendChild(this.btnReset);
        }
        if(this.webcamEnable){
            // Botoes do grupo streaming
            this.btnStreamingToogle = document.createElement('button');this.btnStreamingToogle.classList = 'btn btn-sm btn-outline-secondary';this.btnStreamingToogle.innerHTML = '<i class="fas fa-stop"></i>';this.btnStreamingToogle.title = 'Inicia / para webcam';
            this.btnStreamingToogle.onclick = () => {
                if(this.streaming){this.__stopWebCam();}
                else{this.__startWebCam();}
            };
            this.btnGroupStreaming.appendChild(this.btnStreamingToogle)
            this.btnStreamingSwitchCamera = document.createElement('button');this.btnStreamingSwitchCamera.classList = 'btn btn-sm btn-outline-secondary';this.btnStreamingSwitchCamera.innerHTML = '<i class="fas fa-sync px-2"></i>';this.btnStreamingSwitchCamera.title = 'Alterar Camera';
            this.btnStreamingSwitchCamera.onclick = () => this.__switchCamera();
            this.btnGroupStreaming.appendChild(this.btnStreamingSwitchCamera)
            this.btnStreamingCapture = document.createElement('button');this.btnStreamingCapture.classList = 'btn btn-sm btn-outline-secondary';this.btnStreamingCapture.innerHTML = '<i class="fas fa-camera fa-fw"></i>Capturar';this.btnStreamingCapture.title = 'Capturar imagem';
            this.btnGroupStreaming.appendChild(this.btnStreamingCapture)
            if(__ss == 'sm'){
                this.btnStreamingMobileCapture = document.createElement('button');this.btnStreamingMobileCapture.classList = 'jsPhotoBtnCapture d-none';this.btnStreamingMobileCapture.innerHTML = '<i class="fas fa-camera"></i>';
                this.video.parentNode.appendChild(this.btnStreamingMobileCapture);
                this.btnStreamingMobileCapture.onclick = () => {this.__webcamCapture()};
            }
            this.btnStreamingCapture.onclick = () => {this.__webcamCapture()};
        }
        
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
        // 1) Verifica se cropper esta ativo, se sim gera o dataUrl baseado na area do cropper
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
        if(__ss == 'sm'){this.btnStreamingMobileCapture.classList.remove('d-none');}
        this.bkpImage = this.image.src;
        this.video.classList.remove('d-none'); // Exibe o video
        let self = this;
        navigator.mediaDevices.getUserMedia({video: {facingMode: this.facingMode}, audio: false})
        .then(function(stream){self.video.srcObject = stream;self.video.play();})
        .catch(function(e){console.log(e)});

        this.btnGroupFont.classList.add('d-none');
        this.btnGroupEdit.classList.add('d-none');
        this.btnGroupSave.classList.add('d-none');
        this.modalDismiss.classList.add('d-none');
        this.btnGroupStreaming.classList.remove('d-none');
        this.streaming = true;
        this.btnStreamingToogle.innerHTML = '<i class="fas fa-stop fa-fw"></i>Off';
    }
    __switchCamera(){
        this.__stopWebCam();
        this.facingMode = this.facingMode == 'user' ? 'environment' : 'user';
        this.__startWebCam();
    }
    __stopWebCam(){ // Finaliza gravacao
        if(!this.streaming){return false;}
        let mediaStream = this.video.srcObject;
        let tracks = mediaStream.getTracks();
        tracks[0].stop();
        this.streaming = false;
        this.btnStreamingToogle.innerHTML = '<i class="fas fa-play fa-fw"></i>On';
    }
    __webcamCapture(){ // Captura imagem do canvas e salva em this.image
        if(!this.streaming){return false;}
        let context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0, this.video.videoWidth, this.video.videoHeight);
        let data = this.canvas.toDataURL('image/png');
        this.canvas.src = data; // Atualiza o preview do video
        this.image.src = data; // Atualiza a imagem principal
        this.video.pause();
        this.__stopWebCam();
    }
    __endWebCam(){ // Finaliza as operacoes com captura da webcam
        if(this.streaming){this.__stopWebCam();}
        this.video.classList.add('d-none');
        if(__ss == 'sm'){this.btnStreamingMobileCapture.classList.add('d-none');}
        this.btnGroupStreaming.classList.add('d-none');
        this.img_container.classList.remove('d-none');
        this.btnGroupFont.classList.remove('d-none');
        this.btnGroupEdit.classList.remove('d-none');
        this.btnGroupSave.classList.remove('d-none');
        this.modalDismiss.classList.remove('d-none');
        if(this.cropperEnable){this.__cropImage()}
        this.viewMode = 'default';
        this.jsPhotoInput.value = null;
    }
}