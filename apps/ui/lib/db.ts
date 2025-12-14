/**
 * PostgreSQL database client.
 * Connects to the Goliath Postgres instance for user sync.
 */

import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://goliath:goliath@localhost:5432/goliath',
})

export async function query(text: string, params?: unknown[]) {
  const client = await pool.connect()
  try {
    const result = await client.query(text, params)
    return result
  } finally {
    client.release()
  }
}

export async function upsertUser(user: {
  id: string
  displayName: string
  email?: string
}) {
  const result = await query(
    `INSERT INTO humans (id, display_name, email)
     VALUES ($1, $2, $3)
     ON CONFLICT (id) DO UPDATE SET
       display_name = EXCLUDED.display_name,
       email = EXCLUDED.email
     RETURNING *`,
    [user.id, user.displayName, user.email || null]
  )
  return result.rows[0]
}

export async function getUser(id: string) {
  const result = await query('SELECT * FROM humans WHERE id = $1', [id])
  return result.rows[0] || null
}

export async function deleteUser(id: string) {
  await query('DELETE FROM humans WHERE id = $1', [id])
}

export default pool
