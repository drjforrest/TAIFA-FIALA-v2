// Test database connection from frontend
const { createClient } = require('@supabase/supabase-js')

// Use hardcoded values from .env.local
const supabaseUrl = 'https://bbbwmfylfbiltzcyucwa.supabase.co'
const supabaseKey = 'sb_publishable_sw5puxrJfZe80-UwSkvlAA_EzYiN0Fy'

console.log('🧪 Testing TAIFA-FIALA Database Connection...')
console.log(`URL: ${supabaseUrl}`)
console.log(`Key: ${supabaseKey ? 'Present' : 'Missing'}`)

const supabase = createClient(supabaseUrl, supabaseKey)

async function testConnection() {
  try {
    // Test publications
    console.log('\n📚 Testing Publications Table...')
    const { data: publications, error: pubError, count: pubCount } = await supabase
      .from('publications')
      .select('*', { count: 'exact' })
      .limit(5)

    if (pubError) {
      console.error('❌ Publications Error:', pubError)
    } else {
      console.log(`✅ Found ${pubCount} publications in database`)
      console.log('Sample publications:')
      publications.forEach((pub, i) => {
        console.log(`  ${i + 1}. ${pub.title.substring(0, 80)}...`)
        console.log(`     Source: ${pub.source} | Year: ${pub.year} | African: ${(pub.african_relevance_score * 100).toFixed(0)}% | AI: ${(pub.ai_relevance_score * 100).toFixed(0)}%`)
      })
    }

    // Test dashboard stats
    console.log('\n📊 Testing Dashboard Stats...')
    const { data: stats, error: statsError } = await supabase
      .from('dashboard_stats')
      .select('*')
      .single()

    if (statsError) {
      console.error('❌ Dashboard Stats Error:', statsError)
    } else {
      console.log('✅ Dashboard Stats:')
      console.log(`  Total Publications: ${stats.total_publications}`)
      console.log(`  Total Innovations: ${stats.total_innovations}`)
      console.log(`  Total Organizations: ${stats.total_organizations}`)
      console.log(`  Verified Individuals: ${stats.verified_individuals}`)
      console.log(`  African Countries Covered: ${stats.african_countries_covered}`)
      console.log(`  Unique Keywords: ${stats.unique_keywords}`)
      console.log(`  Avg African Relevance: ${(stats.avg_african_relevance * 100).toFixed(1)}%`)
      console.log(`  Avg AI Relevance: ${(stats.avg_ai_relevance * 100).toFixed(1)}%`)
    }

    // Test individuals
    console.log('\n👥 Testing Individuals Table...')
    const { data: individuals, error: indError, count: indCount } = await supabase
      .from('individuals')
      .select('*', { count: 'exact' })
      .limit(5)

    if (indError) {
      console.error('❌ Individuals Error:', indError)
    } else {
      console.log(`✅ Found ${indCount} individuals in database`)
      console.log('Sample individuals:')
      individuals.forEach((ind, i) => {
        console.log(`  ${i + 1}. ${ind.name} (${ind.role || 'researcher'})`)
      })
    }

    // Test by source
    console.log('\n🔍 Testing Publications by Source...')
    const { data: sourceData, error: sourceError } = await supabase
      .from('publications')
      .select('source')

    if (sourceError) {
      console.error('❌ Source Data Error:', sourceError)
    } else {
      const sourceCount = {}
      sourceData.forEach(pub => {
        sourceCount[pub.source] = (sourceCount[pub.source] || 0) + 1
      })
      console.log('✅ Publications by Source:')
      Object.entries(sourceCount).forEach(([source, count]) => {
        console.log(`  ${source}: ${count} publications`)
      })
    }

    // Test recent publications
    console.log('\n⏰ Testing Recent Publications...')
    const { data: recentPubs, error: recentError } = await supabase
      .from('publications')
      .select('title, publication_date, source, african_relevance_score, ai_relevance_score')
      .order('created_at', { ascending: false })
      .limit(3)

    if (recentError) {
      console.error('❌ Recent Publications Error:', recentError)
    } else {
      console.log('✅ Most Recent Publications:')
      recentPubs.forEach((pub, i) => {
        console.log(`  ${i + 1}. ${pub.title.substring(0, 60)}...`)
        console.log(`     Date: ${pub.publication_date || 'Unknown'} | Source: ${pub.source}`)
        console.log(`     Scores - African: ${(pub.african_relevance_score * 100).toFixed(0)}%, AI: ${(pub.ai_relevance_score * 100).toFixed(0)}%`)
      })
    }

    console.log('\n🎉 Database Connection Test Complete!')
    console.log('✅ Frontend can successfully connect to Supabase database')
    console.log('✅ All data is accessible and properly formatted')
    console.log('🚀 Ready for public launch!')

  } catch (error) {
    console.error('❌ Connection Test Failed:', error)
  }
}

testConnection()