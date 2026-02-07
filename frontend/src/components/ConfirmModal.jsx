import React from "react"

export default function ConfirmModal({
  open,
  title = "Confirm Delete",
  message,
  confirmText = "Delete",
  cancelText = "Cancel",
  onConfirm,
  onCancel
}) {
  // Render nothing when closed so the modal is fully removed from the DOM.
  if (!open) return null

  return (
    // Overlay blocks interaction with the background and centers the modal.
    <div className="modalOverlay">
      <div className="modal">
        <h3>{title}</h3>

        <p>{message}</p>

        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <button onClick={onCancel}>
            {cancelText}
          </button>

          <button className="danger" onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
