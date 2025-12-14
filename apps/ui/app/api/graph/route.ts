import { NextRequest, NextResponse } from 'next/server'
import { Pool } from 'pg'

// Database connection pool
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  database: process.env.POSTGRES_DB || 'goliath',
  user: process.env.POSTGRES_USER || 'goliath',
  password: process.env.POSTGRES_PASSWORD || 'goliath',
  max: 5,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

// Color mapping for node types
const NODE_COLORS: Record<string, string> = {
  human: '#3b82f6',      // Blue
  work_item: '#ef4444',  // Red
  service: '#10b981',    // Green
  decision: '#8b5cf6',   // Purple
  outcome: '#f59e0b',    // Amber
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const nodeType = searchParams.get('node_type')
    const service = searchParams.get('service')
    const limit = parseInt(searchParams.get('limit') || '1000')
    const timeStart = searchParams.get('time_start')
    const timeEnd = searchParams.get('time_end')

    const client = await pool.connect()

    try {
      // Build WHERE clauses for work items
      const workItemsWhereClauses: string[] = []
      const workItemsParams: any[] = []
      let workItemsParamIndex = 1

      if (nodeType === 'work_item' || !nodeType) {
        if (service) {
          workItemsWhereClauses.push(`service = $${workItemsParamIndex}`)
          workItemsParams.push(service)
          workItemsParamIndex++
        }
      }

      const workItemsWhereClause = workItemsWhereClauses.length > 0 
        ? `WHERE ${workItemsWhereClauses.join(' AND ')}` 
        : ''

      // Query nodes: Work Items (only if nodeType is 'work_item' or not specified)
      let workItemsResult: any = { rows: [] }
      if (nodeType === 'work_item' || !nodeType) {
        const workItemsQuery = `
          SELECT 
            id,
            'work_item' as type,
            COALESCE(description, id) as label,
            COALESCE(embedding_3d_x, 0) as x,
            COALESCE(embedding_3d_y, 0) as y,
            COALESCE(embedding_3d_z, 0) as z,
            service,
            severity
          FROM work_items
          ${workItemsWhereClause}
          LIMIT $${workItemsParamIndex}
        `
        workItemsParams.push(limit)
        workItemsResult = await client.query(workItemsQuery, workItemsParams)
      }

      // Query nodes: Humans (only if nodeType is 'human' or not specified)
      let humansResult: any = { rows: [] }
      if (nodeType === 'human' || !nodeType) {
        const humansQuery = `
          SELECT 
            id,
            'human' as type,
            display_name as label,
            COALESCE(embedding_3d_x, 0) as x,
            COALESCE(embedding_3d_y, 0) as y,
            COALESCE(embedding_3d_z, 0) as z
          FROM humans
          LIMIT $1
        `
        humansResult = await client.query(humansQuery, [limit])
      }

      // Query nodes: Decisions (only if nodeType is 'decision' or not specified)
      let decisionsResult: any = { rows: [] }
      if (nodeType === 'decision' || !nodeType) {
        const decisionsQuery = `
          SELECT 
            d.id,
            'decision' as type,
            d.id as label,
            0 as x,
            0 as y,
            0 as z,
            d.work_item_id
          FROM decisions d
          LIMIT $1
        `
        decisionsResult = await client.query(decisionsQuery, [limit])
      }

      // Combine all nodes
      const nodes = [
        ...workItemsResult.rows.map((row: any) => ({
          id: row.id,
          type: 'work_item',
          name: row.label || row.id,
          label: row.label || row.id,
          x: row.x || 0,
          y: row.y || 0,
          z: row.z || 0,
          color: NODE_COLORS.work_item,
          val: 10,
          group: 'work_item',
          metadata: {
            service: row.service,
            severity: row.severity,
          },
        })),
        ...humansResult.rows.map((row: any) => ({
          id: row.id,
          type: 'human',
          name: row.label || row.id,
          label: row.label || row.id,
          x: row.x || 0,
          y: row.y || 0,
          z: row.z || 0,
          color: NODE_COLORS.human,
          val: 8,
          group: 'human',
          metadata: {
            display_name: row.label,
          },
        })),
        ...decisionsResult.rows.map((row: any) => ({
          id: row.id,
          type: 'decision',
          name: row.label || row.id,
          label: row.label || row.id,
          x: row.x || 0,
          y: row.y || 0,
          z: row.z || 0,
          color: NODE_COLORS.decision,
          val: 6,
          group: 'decision',
          metadata: {
            work_item_id: row.work_item_id,
          },
        })),
      ]

      // Query edges: Resolved edges
      const resolvedEdgesWhere = timeStart && timeEnd ? `WHERE resolved_at >= $1 AND resolved_at <= $2` : ''
      const resolvedEdgesQuery = `
        SELECT 
          work_item_id as source,
          human_id as target,
          'RESOLVED' as type,
          resolved_at as timestamp
        FROM resolved_edges
        ${resolvedEdgesWhere}
        LIMIT $${timeStart && timeEnd ? '3' : '1'}
      `
      const resolvedEdgesParams = timeStart && timeEnd ? [timeStart, timeEnd, limit] : [limit]
      const resolvedEdgesResult = await client.query(resolvedEdgesQuery, resolvedEdgesParams)

      // Query edges: Transferred edges
      const transferredEdgesWhere = timeStart && timeEnd ? `WHERE transferred_at >= $1 AND transferred_at <= $2` : ''
      const transferredEdgesQuery = `
        SELECT 
          work_item_id as source,
          to_human_id as target,
          'TRANSFERRED' as type,
          transferred_at as timestamp
        FROM transferred_edges
        ${transferredEdgesWhere}
        LIMIT $${timeStart && timeEnd ? '3' : '1'}
      `
      const transferredEdgesParams = timeStart && timeEnd ? [timeStart, timeEnd, limit] : [limit]
      const transferredEdgesResult = await client.query(transferredEdgesQuery, transferredEdgesParams)

      // Query edges: Co-worked edges
      const coWorkedEdgesWhere = timeStart && timeEnd ? `WHERE worked_at >= $1 AND worked_at <= $2` : ''
      const coWorkedEdgesQuery = `
        SELECT 
          human1_id as source,
          human2_id as target,
          'CO_WORKED' as type,
          worked_at as timestamp,
          work_item_id
        FROM co_worked_edges
        ${coWorkedEdgesWhere}
        LIMIT $${timeStart && timeEnd ? '3' : '1'}
      `
      const coWorkedEdgesParams = timeStart && timeEnd ? [timeStart, timeEnd, limit] : [limit]
      const coWorkedEdgesResult = await client.query(coWorkedEdgesQuery, coWorkedEdgesParams)

      // Also get edges from decisions (work_item -> human assignments)
      const decisionEdgesQuery = `
        SELECT 
          d.work_item_id as source,
          d.primary_human_id as target,
          'ASSIGNED' as type,
          d.created_at as timestamp
        FROM decisions d
        LIMIT $1
      `
      const decisionEdgesResult = await client.query(decisionEdgesQuery, [limit])

      // Combine all edges
      const edges = [
        ...resolvedEdgesResult.rows.map((row: any) => ({
          source: row.source,
          target: row.target,
          type: row.type,
          timestamp: row.timestamp,
        })),
        ...transferredEdgesResult.rows.map((row: any) => ({
          source: row.source,
          target: row.target,
          type: row.type,
          timestamp: row.timestamp,
        })),
        ...coWorkedEdgesResult.rows.map((row: any) => ({
          source: row.source,
          target: row.target,
          type: row.type,
          timestamp: row.timestamp,
        })),
        ...decisionEdgesResult.rows.map((row: any) => ({
          source: row.source,
          target: row.target,
          type: row.type,
          timestamp: row.timestamp,
        })),
      ]

      // Calculate stats
      const stats = {
        total_nodes: nodes.length,
        total_edges: edges.length,
        by_type: {
          human: nodes.filter((n) => n.type === 'human').length,
          work_item: nodes.filter((n) => n.type === 'work_item').length,
          service: nodes.filter((n) => n.type === 'service').length,
          decision: nodes.filter((n) => n.type === 'decision').length,
          outcome: nodes.filter((n) => n.type === 'outcome').length,
        },
      }

      return NextResponse.json({
        nodes,
        links: edges,
        stats,
      })
    } finally {
      client.release()
    }
  } catch (error) {
    console.error('Graph API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch graph data', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

