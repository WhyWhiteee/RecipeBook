import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RecipeCard from '../RecipeCard.vue'

describe('RecipeCard', () => {
  it('renders title from props', () => {
    const wrapper = mount(RecipeCard, {
      props: { title: 'Борщ' }
    })
    expect(wrapper.text()).toContain('Борщ')
    expect(wrapper.find('.card-title').text()).toBe('Борщ')
  })

  it('renders subtitle when provided', () => {
    const wrapper = mount(RecipeCard, {
      props: { title: 'Суп', subtitle: 'Лёгкий обед' }
    })
    expect(wrapper.find('.card-subtitle').exists()).toBe(true)
    expect(wrapper.find('.card-subtitle').text()).toBe('Лёгкий обед')
  })

  it('hides subtitle paragraph when subtitle is empty', () => {
    const wrapper = mount(RecipeCard, {
      props: { title: 'Только заголовок' }
    })
    expect(wrapper.find('.card-subtitle').exists()).toBe(false)
  })

  it('emits delete when delete button is clicked', async () => {
    const wrapper = mount(RecipeCard, {
      props: { title: 'Рецепт' }
    })

    await wrapper.get('[data-testid="delete-recipe"]').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')).toHaveLength(1)
  })

  it('delete button is visible and labeled', () => {
    const wrapper = mount(RecipeCard, {
      props: { title: 'X', subtitle: 'Y' }
    })
    const btn = wrapper.get('.btn-delete')
    expect(btn.text()).toContain('Удалить')
  })
})
