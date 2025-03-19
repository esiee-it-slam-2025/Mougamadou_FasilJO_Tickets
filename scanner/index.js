// Configuration
const API_URL = 'http://127.0.0.1:8000';
let qrScanner;

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Éléments DOM
    const cameraButton = document.getElementById('camera-button');
    const fileButton = document.getElementById('file-button');
    const videoContainer = document.getElementById('video-container');
    const qrVideo = document.getElementById('qr-video');
    const uploadContainer = document.getElementById('upload-container');
    const fileScan = document.getElementById('file-scan');
    const loader = document.getElementById('loader');
    const ticketInfo = document.getElementById('ticket-info');
    const validityStatus = document.getElementById('validity-status');
    const ticketDetails = document.getElementById('ticket-details');

    // Initialisation des événements
    cameraButton.addEventListener('click', startCamera);
    fileButton.addEventListener('click', () => {
        uploadContainer.classList.add('active');
        videoContainer.style.display = 'none';
        if (qrScanner) {
            qrScanner.stop();
        }
    });

    uploadContainer.addEventListener('click', () => {
        fileScan.click();
    });

    fileScan.addEventListener('change', handleFileSelect);

    // Fonction pour démarrer la caméra
    function startCamera() {
        uploadContainer.classList.remove('active');
        videoContainer.style.display = 'block';

        if (!qrScanner) {
            qrScanner = new QrScanner(
                qrVideo,
                result => handleQrCode(result.data)
            );
        }

        qrScanner.start().catch(error => {
            alert('Impossible d\'accéder à la caméra. Erreur: ' + error);
            uploadContainer.classList.add('active');
            videoContainer.style.display = 'none';
        });
    }

    // Fonction pour gérer la sélection de fichier
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        loader.style.display = 'block';

        QrScanner.scanImage(file, { returnDetailedScanResult: true })
            .then(result => {
                handleQrCode(result.data);
            })
            .catch(error => {
                alert('Aucun QR code trouvé dans l\'image ou erreur: ' + error);
            })
            .finally(() => {
                loader.style.display = 'none';
            });
    }

    // Fonction pour gérer le QR code scanné
    async function handleQrCode(data) {
        loader.style.display = 'block';
        ticketInfo.style.display = 'none';

        try {
            let ticketId;
            try {
                const qrData = JSON.parse(data);
                ticketId = qrData.ticketId;
            } catch (e) {
                ticketId = data;
            }

            if (!ticketId) {
                throw new Error('QR code invalide: identifiant du ticket manquant');
            }

            const response = await fetch(`${API_URL}/api/getInfo/${ticketId}/`);

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const ticketData = await response.json();

            // Afficher les informations du ticket
            displayTicketInfo(ticketData);
        } catch (error) {
            console.error('Erreur:', error);
            validityStatus.innerHTML = `
                <div class="ticket-invalid">
                    Billet invalide ou non reconnu
                </div>
            `;
            ticketDetails.innerHTML = `<div><strong>Erreur:</strong> ${error.message || 'Impossible de vérifier ce ticket'}</div>`;
            ticketInfo.style.display = 'block';
        } finally {
            loader.style.display = 'none';
        }
    }

    function displayTicketInfo(ticket) {
        console.log("Ticket data:", ticket); // Debug
        
        const isValid = !ticket.is_used;
        
        validityStatus.innerHTML = isValid ? 
            `<div class="ticket-valid">Billet valide ✓</div>` : 
            `<div class="ticket-invalid">Billet déjà utilisé ✗</div>`;
        
        // Correction des propriétés pour l'affichage
        let matchDate = "Date non disponible";
        if (ticket.event && ticket.event.start) {
            // Convertir la chaîne de date en objet Date
            matchDate = ticket.event.start;
        }
        
        // Gestion des équipes
        let homeTeam = "-";
        let awayTeam = "-";
        
        if (ticket.event) {
            if (ticket.event.team_home && ticket.event.team_home.name) {
                homeTeam = ticket.event.team_home.name;
            }
            if (ticket.event.team_away && ticket.event.team_away.name) {
                awayTeam = ticket.event.team_away.name;
            }
        }
        
        ticketDetails.innerHTML = `
            <div><strong>ID:</strong> ${ticket.id}</div>
            <div><strong>Catégorie:</strong> ${ticket.category}</div>
            <div><strong>Prix:</strong> ${ticket.price}</div>
            <div><strong>Match:</strong> ${homeTeam} vs ${awayTeam}</div>
            <div><strong>Date du match:</strong> ${matchDate}</div>
            <div><strong>Stade:</strong> ${ticket.event?.stadium?.name || '-'}</div>
        `;
        
        if (isValid) {
            ticketDetails.innerHTML += `
                <div class="mark-used" style="grid-column: span 2; text-align: center; margin-top: 1rem;">
                    <button id="mark-used-btn">Marquer comme utilisé</button>
                </div>
            `;
            
            setTimeout(() => {
                document.getElementById('mark-used-btn').addEventListener('click', () => markTicketAsUsed(ticket.id));
            }, 0);
        }
        
        ticketInfo.style.display = 'block';
    }

    async function markTicketAsUsed(ticketId) {
        try {
            loader.style.display = 'block';
            const response = await fetch(`${API_URL}/api/markTicketUsed/${ticketId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                alert('Billet marqué comme utilisé avec succès');
                handleQrCode(ticketId);
            } else {
                alert('Erreur: ' + (result.error || 'Impossible de marquer le billet comme utilisé'));
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de la mise à jour du billet');
        } finally {
            loader.style.display = 'none';
        }
    }
});
