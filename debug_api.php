<?php
// Временный API для отладки
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Подключаем MODX
if (!defined('MODX_CORE_PATH')) {
    require_once dirname(__FILE__) . '/core/config/config.inc.php';
}

$modx = new modX();
$modx->initialize('web');

// Получаем все продукты
$query = $modx->newQuery('modResource');
$query->where([
    'class_key' => 'msProduct',
    'published' => 1,
    'deleted' => 0
]);

$query->select([
    'id',
    'pagetitle',
    'parent'
]);

$products = $modx->getCollection('modResource', $query);

$result = [];
foreach ($products as $product) {
    $result[] = [
        'id' => $product->get('id'),
        'name' => $product->get('pagetitle'),
        'parent' => $product->get('parent')
    ];
}

echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>
