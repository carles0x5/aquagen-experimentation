q = f"'{folder_id}' in parents and trashed=false"
res = self.service.files().list(
    q=q,
    fields="files(name)",
    includeItemsFromAllDrives=True,
    corpora="allDrives",
    supportsAllDrives=True
).execute()