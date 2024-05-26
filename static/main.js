document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour marquer une tâche comme faite
    document.querySelectorAll('.mark-done').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            fetch(`/tasks/${taskId}/mark_done`, { method: 'PUT' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Erreur lors de la mise à jour de la tâche.');
                    }
                });
        });
    });

    // Fonction pour marquer une tâche comme non faite
    document.querySelectorAll('.mark-undone').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            fetch(`/tasks/${taskId}/mark_undone`, { method: 'PUT' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Erreur lors de la mise à jour de la tâche.');
                    }
                });
        });
    });

    // Fonction pour supprimer une tâche
    document.querySelectorAll('.delete-task').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Êtes-vous sûr de vouloir supprimer cette tâche ?')) {
                const taskId = this.getAttribute('data-task-id');
                fetch(`/tasks/${taskId}/delete`, { method: 'DELETE' })
                    .then(response => {
                        if (response.ok) {
                            window.location.reload();
                        } else {
                            alert('Erreur lors de la suppression de la tâche.');
                        }
                    });
            }
        });
    });

    // Fonction pour supprimer un projet
    document.querySelectorAll('.delete-projects').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) {
                const projectId = this.getAttribute('data-projects-id');
                fetch(`/projects/${projectId}/delete`, { method: 'DELETE' })
                    .then(response => {
                        if (response.ok) {
                            window.location.reload();
                        } else {
                            alert('Erreur lors de la suppression du projet.');
                        }
                    });
            }
        });
    });

    // Gestion du formulaire de mise à jour des fonds disponibles
    const fundsForm = document.getElementById('funds-form');
    if (fundsForm) {
        fundsForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(fundsForm);
            fetch('/update_funds', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
              .then(data => {
                  if (data.success) {
                      window.location.reload();
                  } else {
                      alert('Erreur lors de la mise à jour des fonds.');
                  }
              });
        });
    }
});
