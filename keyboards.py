from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


go_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Участвую!', callback_data='start_lottery')
        ]
    ]
    )

check_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='TG Канал', url='tg://resolve?domain=passiora')
    ],
    [
        InlineKeyboardButton(text='Instagram', url='instagram.com/passiorajewelry')
    ],
    [
        InlineKeyboardButton(text='Проверить подписки', callback_data='check_sub')
    ]
]
)

skip_sub_check_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Пропустить', callback_data='skip_sub_check')
    ]
]
)
