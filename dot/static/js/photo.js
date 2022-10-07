// Classe para manipulação de foto, webcam

class jsPhoto{
    constructor(options){
        // Variaveis internas ********
        this.cropper = null; // Aponta para o objeto cropper.js
        this.modal = null; // Aponta para o modal
        this.originalImage = null; // Armazena a imagem original
        this.image = null; // Aponta para o img
        // Configuracao ********
        this.imageSrc = options?.imageSrc || ''; // Caminho da imagem a ser pre carregada (caso exista)
        this.canUploadImage = options?.canUploadImage != undefined ? options.canUploadImage : true; // Habilita / desabilita o input file
        this.webcamEnable = options?.webcamEnable != undefined ? options.webcamEnable : true; // Habilita / desabilita o controle da webcam
        this.cropperEnable = options?.cropperEnable != undefined ? options.cropperEnable : true; // Habilita / desabilita o cropper
        this.cropperShape = options?.cropperShape || 'default'; // Formato de saida para o cropper
        this.save = options?.save || this.__save; // Metodo que responde pela acao do save
        this.inputTarget = options?.inputTarget || null; // Se informado input, ao gravar no modal, salva imagem editada no input
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
        if(this.cropperShape == 'circ'){
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
            modal.addEventListener('shown.bs.modal', () => this.__cropImage());
            modal.addEventListener('hidden.bs.modal', () => this.__cropDestroy());
        }
    }
    __createControls(container){
        let btnGroupFont = document.createElement('div');btnGroupFont.classList = 'btn-group';
        let btnGroupEdit = document.createElement('div');btnGroupEdit.classList = 'btn-group ms-1';
        let btnGroupSave = document.createElement('div');btnGroupSave.classList = 'btn-group ms-1';
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
            btnGroupFont.appendChild(this.btnWebcam);
        }
        // Botoes do grupo edicao....
        this.btnZoomIn = document.createElement('button');this.btnZoomIn.classList = 'btn btn-sm btn-outline-primary d-none d-md-block';this.btnZoomIn.innerHTML = '<i class="fas fa-search-plus"></i>';
        this.btnZoomIn.onclick = () => this.cropper.zoom(0.1);
        this.btnZoomOut = document.createElement('button');this.btnZoomOut.classList = 'btn btn-sm btn-outline-primary d-none d-md-block';this.btnZoomOut.innerHTML = '<i class="fas fa-search-minus"></i>';
        this.btnZoomOut.onclick = () => this.cropper.zoom(-0.1);
        this.btnRotateLeft = document.createElement('button');this.btnRotateLeft.classList = 'btn btn-sm btn-outline-primary';this.btnRotateLeft.innerHTML = '<i class="fas fa-undo"></i>';
        this.btnRotateLeft.onclick = () => this.cropper.rotate(-15);
        this.btnRotateRight = document.createElement('button');this.btnRotateRight.classList = 'btn btn-sm btn-outline-primary';this.btnRotateRight.innerHTML = '<i class="fas fa-redo"></i>';
        this.btnRotateRight.onclick = () => this.cropper.rotate(15);
        this.btnScaleX = document.createElement('button');this.btnScaleX.classList = 'btn btn-sm btn-outline-primary';this.btnScaleX.innerHTML = '<i class="fas fa-arrows-alt-h"></i>';
        this.btnScaleX.onclick = () => this.cropper.scaleX(this.cropper.getImageData().scaleX * -1);
        this.btnScaleY = document.createElement('button');this.btnScaleY.classList = 'btn btn-sm btn-outline-primary';this.btnScaleY.innerHTML = '<i class="fas fa-arrows-alt-v px-1"></i>';
        this.btnScaleY.onclick = () => this.cropper.scaleY(this.cropper.getImageData().scaleY * -1);
        btnGroupEdit.appendChild(this.btnZoomIn);
        btnGroupEdit.appendChild(this.btnZoomOut);
        btnGroupEdit.appendChild(this.btnRotateLeft);
        btnGroupEdit.appendChild(this.btnRotateRight);
        btnGroupEdit.appendChild(this.btnScaleX);
        btnGroupEdit.appendChild(this.btnScaleY);
        // Botoes do grupo extra
        this.btnReset = document.createElement('button');this.btnReset.classList = 'btn btn-sm btn-outline-secondary';this.btnReset.innerHTML = '<i class="fas fa-sync"></i>';
        this.btnReset.onclick = () => this.cropper.reset();
        btnGroupSave.appendChild(this.btnReset);
        this.btnRestoreOriginal = document.createElement('button');this.btnRestoreOriginal.classList = 'btn btn-sm btn-outline-secondary d-none';this.btnRestoreOriginal.innerHTML = '<i class="fas fa-history"></i>';
        this.btnRestoreOriginal.onclick = () => {
            this.image.src = this.originalImage;
            this.btnRestoreOriginal.classList.add('d-none');
            this.originalImage = null;
            this.__cropDestroy();
            this.__cropImage();
        };
        this.btnSavePreview = document.createElement('button');this.btnSavePreview.classList = 'btn btn-sm btn-outline-success';this.btnSavePreview.innerHTML = '<i class="fas fa-save fa-fw"></i>Save';
        this.btnSavePreview.onclick = () => {
            let croppedCanvas = this.cropper.getCroppedCanvas();
            this.originalImage = croppedCanvas.toDataURL();
            if(this.cropperShape == 'circ'){croppedCanvas = this.__getRoundedCanvas(croppedCanvas);}
            this.image.src = croppedCanvas.toDataURL();
            this.__cropDestroy();
            this.__cropImage();
            this.btnRestoreOriginal.classList.remove('d-none');
        };
        btnGroupSave.appendChild(this.btnRestoreOriginal);
        btnGroupSave.appendChild(this.btnSavePreview);
        // --------------------
        
        container.appendChild(btnGroupFont);
        container.appendChild(btnGroupEdit);
        container.appendChild(btnGroupSave);
    }
    __cropImage(){this.cropper = new Cropper(this.image, this.cropperOptions);}
    __cropDestroy(){this.cropper.destroy();}
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