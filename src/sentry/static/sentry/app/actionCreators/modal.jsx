import React from 'react';

import ModalActions from '../actions/modalActions';

/**
 * Show a modal
 */
export function openModal(renderer, options) {
  ModalActions.openModal(renderer, options);
}

/**
 * Close modal
 */
export function closeModal() {
  ModalActions.closeModal();
}

export function openDiffModal(options) {
  import('../components/modals/diffModal')
    .then(mod => mod.default)
    .then(Modal =>
      openModal(deps => <Modal {...deps} {...options} />, {
        modalClassName: 'diff-modal',
      })
    );
}

window.openDiffModal = openDiffModal;
