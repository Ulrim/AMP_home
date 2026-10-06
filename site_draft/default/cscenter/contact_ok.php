<?php
// 견적·기술상담 폼 수신 → 관리자 메일 발송 후 contact.html?sent=1 로 이동 (UTF-8 파일)
// 배포 전: $TO 를 AMP 문의 수신 메일로 바꾼다. 서버 메일 발송(mail) 설정을 확인한다.
$TO   = 'CHANGE_ME@example.com';   // [확인 필요] 문의 수신 주소
$FROM = 'no-reply@amp0404.co.kr';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /default/cscenter/contact.html'); exit; }
if (!empty($_POST['website'])) { header('Location: /default/cscenter/contact.html?sent=1'); exit; } // 스팸봇(honeypot)

function clean($v, $max = 2000) {
    $v = trim((string)$v);
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max, 'UTF-8');
}
function oneline($v, $max = 200) { return str_replace("\n", ' ', clean($v, $max)); }

$labels = ['air'=>'공조부품','battery'=>'이차전지 폐수','recycle'=>'공정수 재순환','aqua'=>'육상양식','pharma'=>'제약·화학','etc'=>'기타'];
$field = isset($labels[$_POST['field'] ?? '']) ? $labels[$_POST['field']] : '기타';
$name = oneline($_POST['name'] ?? '', 50);
$company = oneline($_POST['company'] ?? '', 100);
$tel = oneline($_POST['tel'] ?? '', 40);
$email = oneline($_POST['email'] ?? '', 120);
$water = oneline($_POST['water'] ?? '', 200);
$msg = clean($_POST['msg'] ?? '');

if ($name === '' || $tel === '' || $msg === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || empty($_POST['agree'])) {
    http_response_code(400);
    echo '<!doctype html><meta charset="utf-8"><p>입력값을 확인해 주세요. <a href="javascript:history.back()">돌아가기</a></p>';
    exit;
}

$body = "문의 분야: $field\n성명: $name\n회사명: $company\n연락처: $tel\n이메일: $email\n처리 유량·원수 종류: $water\n\n$msg\n";
$subject = "[홈페이지 문의] $field - $name";
mb_language('uni'); mb_internal_encoding('UTF-8');
$headers = "From: $FROM\r\nReply-To: $email\r\n";
mb_send_mail($TO, $subject, $body, $headers);

header('Location: /default/cscenter/contact.html?sent=1');
exit;
