// 完整的onMounted函数 - 带localStorage优先和API fallback
onMounted(async () => {
    try {
        loading.value = true
        console.log('🔄 GameConfig初始化开始...')

        // === 1. 优先读取localStorage的selectedPlan ===
        const savedPlan = localStorage.getItem('selectedPlan')
        if (savedPlan) {
            try {
                const planData = JSON.parse(savedPlan)
                console.log('✓ 读取到localStorage方案:', planData)

                // 添加到plans列表
                if (planData.sections && planData.sections.length > 0) {
                    const currentPlan = {
                        plan_id: 'current',
                        title: '当前生成的方案',
                        content: planData.sections.map(s => `${s.title}\n${s.content}`).join('\n\n'),
                        created_at: new Date(planData.timestamp || Date.now()).toISOString(),
                        event: planData.event
                    }
                    plans.value.push(currentPlan)
                    form.selectedPlanId = 'current'
                    console.log('✓ 已预填充当前方案')
                }
            } catch (e) {
                console.error('localStorage数据解析失败:', e)
            }
        }

        // === 2. 尝试加载Plans API（带fallback）===
        try {
            console.log('🔃 尝试加载方案列表...')
            const planList = await planApi.listPlans({ event_id: 1 })
            if (planList && Array.isArray(planList) && planList.length > 0) {
                // 过滤掉重复的current
                const apiPlans = planList.filter(p => p.plan_id !== 'current')
                plans.value.push(...apiPlans)
                console.log(`✓ API加载了 ${apiPlans.length} 个方案`)
            }
        } catch (error) {
            console.warn('⚠️ Plans API加载失败，使用本地数据:', error)
        }

        // 如果还没有选中方案，选第一个
        if (!form.selectedPlanId && plans.value.length > 0) {
            form.selectedPlanId = plans.value[0].plan_id
        }

        console.log(`📋 当前可用方案: ${plans.value.length} 个，已选择: ${form.selectedPlanId}`)

        // === 3. 加载Agent Templates（带fallback）===
        try {
            console.log('🔃 尝试加载智能体模板...')
            const [blueTemplates, redTemplates, judgeTemplates] = await Promise.all([
                agentApi.getTemplates('blue').catch(() => []),
                agentApi.getTemplates('red').catch(() => []),
                agentApi.getTemplates('judge').catch(() => [])
            ])
            agentTemplates.value = {
                blue: blueTemplates || [],
                red: redTemplates || [],
                judge: judgeTemplates || []
            }
            console.log('✓ 智能体模板加载完成')
        } catch (error) {
            console.warn('⚠️ Templates API失败，使用空数组:', error)
            agentTemplates.value = { blue: [], red: [], judge: [] }
        }

        // === 4. 加载Created Agents（带fallback）===
        try {
            console.log('🔃 尝试加载智能体实例...')
            const [blueAgents, redAgents, judgeAgents] = await Promise.all([
                agentApi.listAgents({ agent_type: 'blue' }).catch(() => []),
                agentApi.listAgents({ agent_type: 'red' }).catch(() => []),
                agentApi.listAgents({ agent_type: 'judge' }).catch(() => [])
            ])
            agents.value = {
                blue: blueAgents || [],
                red: redAgents || [],
                judge: judgeAgents || []
            }

            // 自动选中第一个
            if (blueAgents.length > 0) form.blueAgents = [blueAgents[0].agent_id]
            if (redAgents.length > 0) form.redAgents = [redAgents[0].agent_id]
            if (judgeAgents.length > 0) form.judgeAgent = judgeAgents[0].agent_id

            console.log('✓ 智能体实例加载完成')
        } catch (error) {
            console.warn('⚠️ Agents API失败，使用空数组:', error)
            agents.value = { blue: [], red: [], judge: [] }
        }

        console.log('✅ GameConfig初始化完成')

        // 显示提示
        if (form.selectedPlanId === 'current') {
            ElMessage.success('已加载S4生成的方案')
        } else if (plans.value.length === 0) {
            ElMessage.warning('未找到可用方案，请先完成S4方案生成')
        }

    } catch (error) {
        console.error('❌ GameConfig初始化失败:', error)
        ElMessage.error('配置初始化失败')
    } finally {
        loading.value = false
    }
})
