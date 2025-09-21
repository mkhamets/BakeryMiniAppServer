<?php
/**
 * MODX Snippet: API Debug
 * Отладочный API для проверки структуры базы данных
 */

// Подключаем MODX
if (!defined('MODX_CORE_PATH')) {
    require_once dirname(__FILE__) . '/core/config/config.inc.php';
}

$modx = new modX();
$modx->initialize('web');

// Устанавливаем заголовки для JSON
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

$debug_info = [];

// 1. Проверяем все ресурсы с class_key = 'msProduct'
$query1 = $modx->newQuery('modResource');
$query1->where(['class_key' => 'msProduct']);
$query1->select(['id', 'pagetitle', 'parent', 'published', 'deleted']);
$products1 = $modx->getCollection('modResource', $query1);
$debug_info['modResource_msProduct'] = count($products1);

// 2. Проверяем все ресурсы с parent в категориях
$query2 = $modx->newQuery('modResource');
$query2->where(['parent:IN' => [16, 17, 18, 19]]);
$query2->select(['id', 'pagetitle', 'parent', 'class_key', 'published', 'deleted']);
$products2 = $modx->getCollection('modResource', $query2);
$debug_info['modResource_in_categories'] = count($products2);

// 3. Проверяем таблицу msProduct
$query3 = $modx->newQuery('msProduct');
$query3->select(['id', 'pagetitle', 'parent', 'published', 'deleted']);
$products3 = $modx->getCollection('msProduct', $query3);
$debug_info['msProduct_table'] = count($products3);

// 4. Показываем первые несколько продуктов
$debug_info['sample_products'] = [];
foreach (array_slice($products2, 0, 3) as $product) {
    $debug_info['sample_products'][] = [
        'id' => $product->get('id'),
        'name' => $product->get('pagetitle'),
        'parent' => $product->get('parent'),
        'class_key' => $product->get('class_key'),
        'published' => $product->get('published'),
        'deleted' => $product->get('deleted')
    ];
}

echo json_encode($debug_info, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>
