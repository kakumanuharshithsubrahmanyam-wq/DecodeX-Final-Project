# Storage bucket: `complaint-attachments`

Create a **private** bucket in Supabase Storage (dashboard or CLI):

```bash
supabase storage buckets create complaint-attachments --public false
```

Object path pattern (enforced by API):

```
{grievance_id}/{attachment_id}/{safe_filename}
```

Policies (dev — tighten for production):

- Citizens may upload only to paths for grievances they own (via signed URL issued by backend).
- Officers read via signed download URLs from backend.
- No public `anon` read on bucket.

Backend uses `SUPABASE_SERVICE_ROLE_KEY` only on the server to sign URLs and verify uploads.
